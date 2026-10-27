"""Runtime descriptors shared by every protocol family and by generated code.

Generated API modules contain only data built from these types (``ApiInfo``,
``Operation``, bindings, models) plus thin methods. All behaviour lives in the
protocol modules, which are sans-IO: a call is a generator that yields
``Request`` values and receives ``Response`` values.
"""

from __future__ import annotations

import collections.abc
import math
import re
from collections.abc import Callable, Generator, Iterable, Mapping
from dataclasses import dataclass, field
from enum import Enum
from functools import cache
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

from .._http.debug import _NAME_KEYS, DEPTH_LIMIT, MAX_DEPTH, _local, is_secret_parameter, serialize
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
    display_text,
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

    _PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"([0-9]{1,18})\.([0-9]{1,18})")

    @classmethod
    def parse(cls, text: str) -> ApiVersion:
        match = cls._PATTERN.fullmatch(text.strip())
        if match is None:
            raise ValueError("Not a major.minor version")
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


def _wire_name(field: Any) -> str | None:
    for alias in (field.validation_alias, field.serialization_alias, field.alias):
        if isinstance(alias, str):
            return alias
    return None


def _repr_value(value: Any, depth: int = 0) -> Any:
    """``value`` as ``repr`` shows it. Plain dicts go through the request-hook serializer (``serialize``: key and value
    redaction, name/value pairs, the depth limit), so repr and the hook records cannot diverge; lists are walked only to
    reach the dicts and models in them (a model masks its own fields), and anything deeper than the limit is a fixed
    placeholder, never the raw subtree."""
    if depth > MAX_DEPTH:
        return DEPTH_LIMIT
    if isinstance(value, dict):
        return serialize(value, None, depth)
    if isinstance(value, list):
        return [_repr_value(item, depth + 1) for item in value]
    if isinstance(value, tuple):
        return tuple(_repr_value(item, depth + 1) for item in value)
    return value


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
    def masked_wire_names(cls) -> frozenset[str]:
        """Wire names (aliases included, nested models too) of the ``x-masked`` fields of this request model.

        The debug hooks redact exactly these names in the record of an operation that uses the model; the same
        name in another operation is not affected. A name with a ``{placeholder}`` stays a template.
        """
        return _masked_wire_names(cls)

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
        if _has_non_finite(data):
            raise ValueError("NaN and infinity cannot be sent: JSON has no representation for them")
        names = cls._wire_to_field()
        unknown = sorted(str(key) for key in data if key not in names)
        if unknown:
            raise ValueError(f"unexpected field(s): {', '.join(unknown)}")
        nulls = sorted(names[k] for k, v in data.items() if v is None and names[k] not in cls.__nullable__)
        if nulls:
            raise ValueError(f"field(s) cannot be null; leave them unset instead: {', '.join(nulls)}")
        return data

    @field_validator("*", mode="before")
    @classmethod
    def _strict_scalar_kinds(cls, value: Any, info: ValidationInfo) -> Any:
        """Requests are strict about booleans: a bool is not a number, and a boolean field takes only a real bool."""
        if info.field_name is None or is_response(info) or value is None:
            return value
        problem = _scalar_problem(cls.model_fields[info.field_name].annotation, value)
        if problem:
            raise ValueError(problem)
        return _as_json_containers(value)  # any Mapping / Sequence that passed is serialized as the dict / list it stands for

    @field_validator("*", mode="wrap")
    @classmethod
    def _tolerate_new_enum_values(cls, value: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo) -> Any:
        try:
            return handler(value)
        except ValidationError as original:
            context = info.context or {}
            response = bool(context.get(RESPONSE_CONTEXT))
            collector = context.get(_ROUND_TRIP)
            allowed = context.get(_ALLOWED_VALUES)
            if info.field_name is None or not (response or collector is not None or allowed is not None):
                raise
            field = cls.model_fields[info.field_name]
            annotation = Annotated[(field.annotation, *field.metadata)] if field.metadata else field.annotation
            if response:
                coerced = _coerce_text(annotation, value)
                if coerced is not value:
                    try:
                        return handler(coerced)
                    except ValidationError:
                        value = coerced
            new: list[Any] = []
            try:
                result = lenient_value(annotation, value, context, new)
            except (ValidationError, _NoMatch):
                raise original from None
            if not new:
                raise original  # no unknown enum value: some other constraint failed (for example an emptied list)
            if response:
                return result
            pairs = [(cls, info.field_name, item) for item in new]
            if collector is not None:
                collector.update(pairs)
                return result
            if allowed is not None and all(pair in allowed for pair in pairs):
                return result
            raise original

    def __repr_args__(self) -> Iterable[tuple[str | None, Any]]:
        fields_set = self.model_fields_set
        masked = self.__masked__
        shown = [(name, value) for name, value in super().__repr_args__() if name in fields_set or value is not None]
        wire = {name: _wire_name(field) or name for name, field in type(self).model_fields.items()}
        # ``Name`` / ``Value`` pairs (action and recipient parameters): a secret-named parameter hides its sibling value,
        # exactly as the request-hook serializer does it.
        parameter = is_secret_parameter((wire.get(str(name), str(name)), value) for name, value in shown)
        for name, value in shown:
            if value is not None and (name in masked or (parameter and _local(wire.get(str(name), str(name))) == "value")):
                yield name, _MASKED_REPR
            else:
                yield name, _repr_value(value)

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
        carried = self._round_trip_values | _nested_round_trip_values(self)  # a nested ``from_current`` model brings its own
        model = type(self).model_validate(data, context={_ALLOWED_VALUES: carried})
        model._round_trip_values = carried
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


def _nested_round_trip_values(value: Any) -> frozenset[Any]:
    """The carried unknown enum values of every model inside ``value`` (nested models, lists, tuples and mappings)."""
    if isinstance(value, Model):
        found = set(value._round_trip_values)
        for name in value.model_fields_set:
            found |= _nested_round_trip_values(getattr(value, name))
        return frozenset(found)
    if isinstance(value, (list, tuple)):
        return frozenset().union(*(_nested_round_trip_values(item) for item in value))
    if isinstance(value, dict):
        return frozenset().union(*(_nested_round_trip_values(item) for item in value.values()))
    return frozenset()


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


class _NoMatch(Exception):
    """A value does not fit the annotation, even with unknown enum values allowed."""


def lenient_value(annotation: Any, value: Any, context: Mapping[str, Any], new: list[Any]) -> Any:
    """Validate ``value`` against ``annotation``, accepting enum values the generated ``Literal`` does not list.

    Works through ``Annotated``, unions, lists and mappings of any depth; every unknown member (same primitive
    type as the listed ones, never ``null`` or an object) is appended to ``new``. ``const`` fields stay strict.
    Anything that is not an enum position (models, scalars) is validated normally under ``context``, so a model
    inside a mapping or list applies its own tolerance. Raises ``_NoMatch`` or ``ValidationError`` if ``value`` fits
    nowhere.
    """
    origin = get_origin(annotation)
    if origin is Annotated:
        base, *metadata = get_args(annotation)
        if any(m is CONST for m in metadata):
            return _validate(annotation, value, context)
        result = lenient_value(base, value, context, new)
        # Only the enum values are lenient: every other constraint (length, range, pattern) still applies.
        return _validate(Annotated[(_widen(base), *metadata)], result, context)
    if origin in (Union, UnionType):
        for arm in get_args(annotation):
            if arm is type(None):
                if value is None:
                    return None
                continue
            found: list[Any] = []
            try:
                result = lenient_value(arm, value, context, found)
            except (ValidationError, _NoMatch):
                continue
            new.extend(found)
            return result
        raise _NoMatch
    if origin is list:
        (item,) = get_args(annotation) or (Any,)
        if not isinstance(value, list):
            raise _NoMatch
        return [lenient_value(item, v, context, new) for v in value]
    if origin in (dict, Mapping):
        key, item = get_args(annotation) or (Any, Any)
        if not isinstance(value, dict):
            raise _NoMatch
        return {lenient_value(key, k, context, new): lenient_value(item, v, context, new) for k, v in value.items()}
    if origin is Literal:
        values = get_args(annotation)
        if context.get(RESPONSE_CONTEXT):
            value = _coerce_text(annotation, value)
        if value in values and type(value) in {type(v) for v in values}:
            return value
        if value is not None and type(value) in {type(v) for v in values}:
            new.append(value)
            return value
        raise _NoMatch
    return _validate(annotation, value, context)


def _widen(annotation: Any) -> Any:
    """``annotation`` with every (non-``const``) ``Literal`` replaced by the types of its values."""
    origin = get_origin(annotation)
    if origin is Annotated:
        base, *metadata = get_args(annotation)
        if any(m is CONST for m in metadata):
            return annotation
        return Annotated[(_widen(base), *metadata)]
    if origin in (Union, UnionType):
        return Union[tuple(_widen(arg) for arg in get_args(annotation))]  # noqa: UP007
    if origin is list:
        return list[_widen(get_args(annotation)[0])] if get_args(annotation) else annotation
    if origin in (dict, Mapping) and len(get_args(annotation)) == 2:
        key, item = get_args(annotation)
        return dict[_widen(key), _widen(item)]
    if origin is Literal:
        kinds = tuple(dict.fromkeys(type(v) for v in get_args(annotation)))
        return Union[kinds]  # noqa: UP007
    return annotation


def _validate(annotation: Any, value: Any, context: Mapping[str, Any]) -> Any:
    try:
        checker = adapter(annotation)
    except TypeError:  # unhashable annotation (metadata): not cached
        checker = TypeAdapter(annotation)
    return checker.validate_python(value, context=dict(context))


def _container(annotation: Any, kinds: tuple[Any, ...]) -> Any:
    """The ``list[...]``/``dict[...]`` part of an annotation, looking through ``Annotated`` and unions (else ``None``)."""
    origin = get_origin(annotation)
    if origin in kinds:
        return annotation
    if origin in (Annotated, Union, UnionType):
        for arg in get_args(annotation):
            found = _container(arg, kinds)
            if found is not None:
                return found
    return None


_INT_TEXT = re.compile(r"[+-]?[0-9]{1,18}")  # bounded: int() of thousands of digits raises ValueError


def _coerce_text(annotation: Any, value: Any) -> Any:
    """Turn text from XML or ``key=value`` replies into the integer a ``Literal[1, 2]`` field lists.

    Only strings that spell an integer, for fields that are integer enums, are
    converted (also inside lists); everything else is returned unchanged.
    """
    if isinstance(value, list):
        (inner,) = get_args(_container(annotation, (list,))) or (Any,)
        return [_coerce_text(inner, v) for v in value]
    if isinstance(value, dict):
        inner = (get_args(_container(annotation, (dict, Mapping))) or (Any, Any))[1]
        return {k: _coerce_text(inner, v) for k, v in value.items()}
    if isinstance(value, str) and _INT_TEXT.fullmatch(value.strip()):
        values = _literal_values(annotation)
        if values and any(isinstance(v, int) and not isinstance(v, bool) for v in values):
            return int(value)
    return value


@cache
def _masked_wire_names(model: type[Model]) -> frozenset[str]:
    names: set[str] = set()
    seen: set[type] = set()

    def walk_annotation(annotation: Any) -> None:
        if isinstance(annotation, type) and issubclass(annotation, Model):
            walk(annotation)
        for arg in get_args(annotation):
            walk_annotation(arg)

    def walk(cls: type[Model]) -> None:
        if cls in seen:
            return
        seen.add(cls)
        for name, info in cls.model_fields.items():
            if name in cls.__masked__:
                names.add(name)
                for alias in (info.alias, info.validation_alias, info.serialization_alias):
                    if isinstance(alias, str):
                        names.add(alias)
            walk_annotation(info.annotation)

    walk(model)
    return frozenset(names)


def _scalar_problem(annotation: Any, value: Any) -> str | None:
    """Why ``value`` is the wrong *kind* for a request field, or ``None``.

    A request is strict about what a boolean is: a bool is not a number (or text), a boolean field takes only a real
    bool, and an integer field refuses a fraction (``2.0`` is accepted as 2, ``2.5`` is not). Text that spells a number
    is still accepted (the CLI passes text). The rule applies at every depth: list, tuple (fixed and variadic), set and
    mapping items, ``Annotated``, ``Literal`` and unions (accepted if any branch accepts). Nested models check their own
    fields when pydantic validates them. Anything not described here is left to pydantic."""
    origin = get_origin(annotation)
    if value is None or annotation is Any:
        return None
    if origin is Annotated:
        return _scalar_problem(get_args(annotation)[0], value)
    if origin in (Union, UnionType):
        problems = []
        for arm in get_args(annotation):
            if arm is type(None):
                continue
            problem = _scalar_problem(arm, value)
            if problem is None:
                return None  # one branch accepts it
            problems.append(problem)
        return problems[0] if problems else None
    if origin is Literal:
        literals = get_args(annotation)
        if isinstance(value, bool):
            return None if any(isinstance(v, bool) for v in literals) else "a boolean is not one of the allowed values"
        return None
    if origin in (list, set, frozenset, collections.abc.Sequence, collections.abc.Set):
        if not _is_list_like(value):
            return f"expected a list, got {kind_of(value)}"  # in a union this branch must not accept a scalar
        args = get_args(annotation)
        return _first_problem((args[0], entry) for entry in value) if args else None
    if origin is tuple:
        if not _is_list_like(value):
            return f"expected a list, got {kind_of(value)}"
        args = get_args(annotation)
        if not args:
            return None
        if len(args) == 2 and args[1] is Ellipsis:
            return _first_problem((args[0], entry) for entry in value)
        return _first_problem(zip(args, value, strict=False))
    if origin in (dict, collections.abc.Mapping):
        if not isinstance(value, collections.abc.Mapping):
            return f"expected an object, got {kind_of(value)}"
        args = get_args(annotation)
        if len(args) != 2:
            return None
        pairs = [pair for key, entry in value.items() for pair in ((args[0], key), (args[1], entry))]
        return _first_problem(pairs)
    if annotation in (bool, int, float, str) and (_is_list_like(value) or isinstance(value, collections.abc.Mapping)):
        return f"expected a single value, got {kind_of(value)}"  # in a union a scalar branch must not accept a container
    if annotation is bool:
        return None if isinstance(value, bool) else f"expected true or false, got {kind_of(value)}"
    if annotation in (int, float):
        if isinstance(value, bool):
            return "a boolean is not a number"
        if annotation is int and isinstance(value, float) and not value.is_integer():
            return "expected a whole number, got a fractional one"
        return None
    if annotation is str:
        return "a boolean is not text" if isinstance(value, bool) else None
    return None


def _is_list_like(value: Any) -> bool:
    """A list, tuple, set or any other ``Sequence`` / ``Set`` implementation; never text or bytes."""
    if isinstance(value, (str, bytes, bytearray)):
        return False
    return isinstance(value, (list, tuple, set, frozenset, collections.abc.Sequence, collections.abc.Set))


def _as_json_containers(value: Any) -> Any:
    """``value`` with every non-builtin Mapping turned into a ``dict`` and every other non-builtin sequence or set into a
    ``list``, at any depth (builtin containers keep their type), so serialization sees plain JSON containers."""
    if isinstance(value, dict):
        return {key: _as_json_containers(item) for key, item in value.items()}
    if isinstance(value, collections.abc.Mapping):
        return {key: _as_json_containers(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        if isinstance(value, (set, frozenset)):
            return value
        converted = [_as_json_containers(item) for item in value]
        return tuple(converted) if isinstance(value, tuple) else converted
    if _is_list_like(value):
        return [_as_json_containers(item) for item in value]
    return value


def _first_problem(pairs: Any) -> str | None:
    for annotation, value in pairs:
        problem = _scalar_problem(annotation, value)
        if problem:
            return problem
    return None


def _has_non_finite(value: Any) -> bool:
    """Whether a request payload holds a NaN or infinite float, at any depth."""
    if isinstance(value, float):
        return not math.isfinite(value)
    if isinstance(value, collections.abc.Mapping):
        return any(_has_non_finite(item) for item in value.values())
    if _is_list_like(value):
        return any(_has_non_finite(item) for item in value)
    return False


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
    """Validate response data against the operation's result type (and refuse non-finite numbers, whatever the protocol)."""
    try:
        result = _validated_result(op, data)
    except RecursionError:  # a pathologically nested answer: a malformed response, not a crash
        raise ResponseFormatError(op.api.id, op.id, "the response is nested too deeply") from None
    if _holds_non_finite(result):
        raise ResponseFormatError(op.api.id, op.id, "the response holds a NaN or infinite number, which no device reports")
    return result


def _holds_non_finite(value: Any) -> bool:
    """Whether a parsed result holds a NaN or infinite float at any depth (models, lists, tuples, sets, mappings).
    Text such as ``"NaN"`` or ``"inf"`` is coerced into a float by pydantic, so this looks at the parsed values.
    Iterative, so a deeply nested answer cannot exhaust the stack."""
    stack = [value]
    while stack:
        item = stack.pop()
        if isinstance(item, float):
            if not math.isfinite(item):
                return True
        elif isinstance(item, BaseModel):
            stack.extend(getattr(item, name) for name in type(item).model_fields)
        elif isinstance(item, dict):
            stack.extend(item.values())
        elif isinstance(item, (list, tuple, set, frozenset)):
            stack.extend(item)
    return False


BODY_OMITTED = "body omitted (operation returns secret fields)"


def has_masked_fields(tp: Any) -> bool:
    """Whether a result type holds an ``x-masked`` field anywhere (models, lists, dicts, unions, optionals, nested).
    Such an operation never puts any part of a response body into an error: the body that failed validation is the
    one place where masking by schema cannot be trusted to find every secret (wrong shapes, renamed keys)."""
    try:
        return _has_masked(tp)
    except TypeError:  # an unhashable annotation (metadata): compute without the cache
        return _scan_masked(tp, set())


@cache
def _has_masked(tp: Any) -> bool:
    return _scan_masked(tp, set())


def _scan_masked(tp: Any, seen: set[Any]) -> bool:
    if isinstance(tp, type) and issubclass(tp, BaseModel):
        if tp in seen:
            return False
        seen.add(tp)
        if getattr(tp, "__masked__", None):
            return True
        return any(_scan_masked(field.annotation, seen) for field in tp.model_fields.values())
    return any(_scan_masked(arg, seen) for arg in get_args(tp) if arg is not type(None) and not isinstance(arg, str))


def redact_text(value: Any, limit: int = 200) -> str:
    """Text for an error message from device data: ``display_text`` with a tighter bound (redaction of secret-looking
    names and URL credentials, control characters escaped). For places that have no operation (the handshake)."""
    return display_text(value, limit)


MESSAGE_OMITTED = "device message omitted (operation handles secret fields)"
CODE_OMITTED = "device error code omitted (operation handles secret fields)"


def has_parameter_pairs(tp: Any) -> bool:
    """Whether a type holds, at any depth, a name/value-pair model: one with a name-like field (``Name``, ``@Name``,
    ``tt:Key``) and a value-like field (``Value``, ``@Value``). Whether a pair carries a secret is decided by the NAME at
    run time (``password``), which no schema can say; so statically, fail closed: an operation that can carry such pairs
    in its request or result is treated as handling secrets."""
    try:
        return _has_parameter_pairs(tp)
    except TypeError:  # an unhashable annotation (metadata): compute without the cache
        return _scan_pairs(tp, set())


@cache
def _has_parameter_pairs(tp: Any) -> bool:
    return _scan_pairs(tp, set())


def _scan_pairs(tp: Any, seen: set[Any]) -> bool:
    if isinstance(tp, type) and issubclass(tp, BaseModel):
        if tp in seen:
            return False
        seen.add(tp)
        locals_ = {_local(_wire_name(field) or name) for name, field in tp.model_fields.items()}
        if locals_ & _NAME_KEYS and "value" in locals_:
            return True
        return any(_scan_pairs(field.annotation, seen) for field in tp.model_fields.values())
    return any(_scan_pairs(arg, seen) for arg in get_args(tp) if arg is not type(None) and not isinstance(arg, str))


def has_secret_fields(op: Operation[Any]) -> bool:
    """Whether the operation handles secrets: masked fields in its result OR in its request params (a request that sends
    a key can have it echoed in a device error), or name/value-pair models in either (a parameter named ``password``
    carries its secret in ``Value``). For such an operation no device text enters an error."""
    params = getattr(op, "params", None)
    result = getattr(op, "result", None)
    return (
        has_masked_fields(result)
        or (params is not None and bool(params.masked_wire_names()))
        or has_parameter_pairs(result)
        or (params is not None and has_parameter_pairs(params))
    )


_ASCII_INT = re.compile(r"[0-9]{1,18}")


def ascii_int(text: str) -> int | None:
    """``text`` as a non-negative integer, or ``None`` if it is not one: ASCII digits only, at most 18 of them.

    THE conversion of device-supplied numeric text. ``str.isdigit()`` is true for superscripts and other Unicode digits
    that ``int()`` refuses, and ``int()`` refuses a string of more than about 4300 digits: both raise ``ValueError``
    from inside a decoder, which would escape the library's error hierarchy. A longer or odd string is simply not a
    number (an error code that is not numeric is looked up as text).
    """
    stripped = text.strip()
    return int(stripped) if _ASCII_INT.fullmatch(stripped) else None


def kind_of(value: Any) -> str:
    """What a malformed device value was, for an error message: its JSON type, never the value itself. A device value
    that is not text must not be turned into text first (``str``, ``repr`` or an f-string): the repr of a mapping has
    no ``name=value`` pair for the redactor to find, so a secret in it would reach the message."""
    return (
        "null" if value is None else "a boolean" if isinstance(value, bool) else "a number" if isinstance(value, (int, float))
        else "text" if isinstance(value, str) else "a list" if isinstance(value, (list, tuple)) else "an object" if isinstance(value, Mapping)
        else type(value).__name__
    )


def error_text(op: Operation[Any], raw: Any, limit: int = 1000) -> str:
    """THE way device-provided error text (an envelope message, an ``Error:`` line) enters an exception message. The raw
    text is used only to look up the error code and kind; what the exception shows is built here: nothing of it for an
    operation that handles secret fields, otherwise the text through the hook redactor (secret-name pairs such as
    ``password=...``, URL credentials)."""
    if has_secret_fields(op):
        return MESSAGE_OMITTED
    return redact_text(raw, limit) if isinstance(raw, str) else kind_of(raw)


def body_excerpt(op: Operation[Any], value: Any) -> str:
    """THE way response body text enters an exception message: none at all for an operation that returns secret
    fields, otherwise a bounded, redacted excerpt. Nothing else may put raw body text into an error (a test scans
    the package for it)."""
    return BODY_OMITTED if has_secret_fields(op) else redact_text(value)


def _safe_details(op: Operation[Any], details: Any) -> Any:
    """``details`` of an API error: structured error objects stay structured (redacted); raw text is bounded and
    redacted; an operation that returns secret fields keeps none of it."""
    if has_secret_fields(op):
        return BODY_OMITTED
    if details is None or isinstance(details, (int, float, bool)):
        return details
    if isinstance(details, str):
        return redact_text(details, 2000)
    try:
        return serialize(details)
    except (TypeError, ValueError, RecursionError):
        return "<unprintable>"


def _shape_message(error: ValidationError, data: Any, op: Operation[Any]) -> str:
    """Why a response does not match, with a bounded excerpt of what the device sent. Pydantic's own text can echo the
    input, so the message is built from the problems only: the location parts and the reason, each put through
    ``display_text`` (a mapping key in a location, or a field name in a validator's text, is the device's), and never
    the ``input``. For an operation that handles secret fields only the declared top-level field and the error type
    are shown."""
    problems: list[str] = []
    for item in error.errors(include_input=False):
        loc = item["loc"]
        if has_secret_fields(op):  # only names the models declare (ours) and list positions; the error type, never its text
            where = ".".join(_declared_part(op, part) for part in loc) or "result"
            problems.append(f"{where}: {item['type']}")
        else:
            where = ".".join(display_text(str(part), 60) for part in loc) or "result"
            problems.append(f"{where}: {display_text(item['msg'], 200)}")
    return f"response does not match the documented shape: {'; '.join(problems)[:400]} (response: {body_excerpt(op, data)})"


def _declared_part(op: Operation[Any], part: Any) -> str:
    """A location part shown for a secret-handling operation: a field name or alias some model of the result declares,
    or a list position; anything else (a mapping key the device chose) is ``*``."""
    if isinstance(part, int):
        return str(part)
    return part if isinstance(part, str) and part in _declared_names(getattr(op, "result", None)) else "*"


def _declared_names(tp: Any) -> frozenset[str]:
    try:
        return _declared_names_cached(tp)
    except TypeError:  # an unhashable annotation
        return frozenset(_collect_names(tp, set()))


@cache
def _declared_names_cached(tp: Any) -> frozenset[str]:
    return frozenset(_collect_names(tp, set()))


def _collect_names(tp: Any, seen: set[Any]) -> set[str]:
    names: set[str] = set()
    if isinstance(tp, type) and issubclass(tp, BaseModel):
        if tp in seen:
            return names
        seen.add(tp)
        for key, field in tp.model_fields.items():
            names |= {key, *(alias for alias in (field.alias, field.validation_alias) if isinstance(alias, str))}
            names |= _collect_names(field.annotation, seen)
        return names
    for arg in get_args(tp):
        if arg is not type(None) and not isinstance(arg, str):
            names |= _collect_names(arg, seen)
    return names


def _validated_result(op: Operation[Any], data: Any) -> Any:
    if op.result is None:
        return None
    try:
        return adapter(op.result).validate_python(data, context={RESPONSE_CONTEXT: True})
    except ValidationError as error:
        new: list[Any] = []
        try:  # newer firmware may add an enum value anywhere in the result: a scalar, a list, a mapping, a union
            tolerated = lenient_value(op.result, data, {RESPONSE_CONTEXT: True}, new)
        except (ValidationError, _NoMatch):
            new = []  # the tolerant pass failed too: report the original error, never a placeholder
        else:
            if new:
                return tolerated
        message = _shape_message(error, data, op)
    # Raised outside the handler, so the pydantic error (which prints the offending input, secrets included) is neither
    # the cause nor the context of this one: no traceback, log record or attribute of it can show the response body.
    raise ResponseFormatError(op.api.id, op.id, message)


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
    status: Literal["released", "beta", "alpha", "deprecated"] = "released"
    """Lifecycle status of the documented API, from the spec."""
    requires_firmware: str | None = None
    """Minimum AXIS OS version (the spec's ``requires.firmware``): ``Device.supports`` answers ``NO`` below it."""
    requires_application: str | None = None
    """The application the spec's ``requires.application`` names (free text, informational; not checked)."""


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

    def error_code(self, code: int | str | None, message: str | None = None, sub_code: int | str | None = None) -> ErrorCode | None:
        """The documented error for ``code``; without a code (or when it is unknown), the one matching ``message``.

        ``sub_code`` (``details.subCode``) selects a composite ``"<code>/subCode <n>"`` entry before the plain code.
        An exact key wins over a range key (``"9000-9999"``); the operation's table wins over the API's.
        """
        if code is not None and sub_code is not None:  # "4004/subCode 202" is more specific than "4004"
            for table in (self.errors, self.api.errors):
                entry = table.get(f"{code}/subCode {sub_code}")
                if entry is not None and entry.message is None and entry.message_prefix is None:
                    return entry
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
    return ascii_int(code)


def _plain_code(op: Operation[Any], code: str) -> bool:
    """Whether a text error code is one of ours: a documented key of the operation's or the API's error table (it comes
    from the spec, not from the device), or plain digits."""
    return _ASCII_INT.fullmatch(code.strip()) is not None or any(code in table for table in (getattr(op, "errors", None) or {}, getattr(op.api, "errors", None) or {}))


def _sub_code(details: Any) -> int | str | None:
    """``subCode`` of an error object (its own member, or inside its ``details``); of the first one in a list."""
    if isinstance(details, list):
        details = details[0] if details else None
    if not isinstance(details, dict):
        return None
    for holder in (details, details.get("details")):
        if isinstance(holder, dict):
            value = holder.get("subCode", holder.get("subcode"))
            if isinstance(value, (int, str)) and not isinstance(value, bool):
                return value
    return None


def api_error(op: Operation[Any], code: Any, message: Any, *, http_status: int | None, details: Any) -> DeviceError:
    """Build the right error for an API error reported by the device.

    ``code`` and ``message`` are the device's raw values: a protocol passes them on without ``str()`` or an f-string, and
    anything but an integer or text code and a text message is a ``ResponseFormatError`` that names only the types.

    One rule for every protocol: **the HTTP status decides the category** when it fixes one. 401 is ``AuthError``,
    403 ``ApiAccessDenied`` (an ``AccessDenied``), 503 ``ApiUnavailable`` (an ``Unavailable``); a 401 is an ``AuthError``
    unless it is a message-keyed error the spec documents (a text ``Error:`` line on a 401). The documented code and description are kept on the
    exception (``code``, ``description``, ``details``) and the documented ``kind`` stays as its refinement. Only when the status fixes no category (a 2xx
    envelope, 404 and the other non-auth 4xx) does the documented ``kind`` pick the class (a 500 fixes none: SOAP carries every fault in a 500).
    """
    if isinstance(code, bool) or not (code is None or isinstance(code, (int, str))) or not isinstance(message, str):
        # The device sent an error object whose fields are not what the protocol allows: never look it up in the
        # error tables. The HTTP status still decides the category where it fixes one; otherwise it is a format error.
        if http_status in (401, 403, 503):
            code, message = None, "the device sent a malformed error object"
        else:
            return ResponseFormatError(op.api.id, op.id, f"malformed error object: code is {kind_of(code)}, message is {kind_of(message)}")
    info = op.error_code(code, message, _sub_code(details))
    documented = info.kind if info else None
    # A 401 stays an API error only for the message-keyed errors a spec labels as such (add_user: "initial admin user
    # must be created first", HTTP 401); a documented numeric code on a 401 is still an authentication failure.
    message_keyed = info is not None and (info.message is not None or info.message_prefix is not None)
    if http_status == 401 and not message_keyed:
        reason = f" ({error_text(op, message)})" if message else ""
        return AuthError(f"{op.api.id}.{op.id}: the device requires authentication and no usable credentials were configured{reason}")
    if http_status == 403:
        category = "access_denied"
    elif http_status == 503:
        category = "unavailable"
    else:
        category = documented  # 2xx envelopes, 404 and other 4xx, and 5xx other than 503 (SOAP sends every fault as 500)
    kind = documented or category
    cls = {"access_denied": ApiAccessDenied, "unavailable": ApiUnavailable}.get(category or "", ApiError)
    # The raw message served the lookups above; the exception shows only what error_text() allows.
    if has_secret_fields(op):
        shown = f"{info.description}: {MESSAGE_OMITTED}" if info and info.description else MESSAGE_OMITTED
    else:
        shown = error_text(op, message)
    if isinstance(code, str) and not _plain_code(op, code):
        # Matching used the raw code above. The public ``code`` of an unrecognised text code is the device's text: for an
        # operation that handles secret fields it is not kept at all (a fixed marker says so), otherwise ApiError stores
        # its ``display_text`` form.
        if has_secret_fields(op):
            code = None
            shown = f"{CODE_OMITTED}; {shown}"
    return cls(
        op.api.id,
        op.id,
        code,
        shown,
        description=info.description if info else None,
        kind=kind,
        http_status=http_status,
        details=_safe_details(op, details),
    )


def http_error(op: Operation[Any], response: Response, *, documented: bool | frozenset[int] = False) -> DeviceError:
    """Build the error for a failure status that carried no API error envelope.

    With ``documented=True`` (rest, whose error maps are keyed by HTTP status) a status the operation or API
    documents wins over the generic mapping below; a set of statuses (cgi: ``{404}``) limits that to those
    statuses. 401 and 403 always keep ``AuthError`` / ``AccessDenied``. Elsewhere the map is keyed by API error
    codes (a CGI map may mix both), so a number that happens to equal an HTTP status must not be taken for it."""
    status = response.status
    if (documented is True or (not isinstance(documented, bool) and status in documented)) and status not in (401, 403) and op.error_code(status) is not None:
        # The operation documents this status (for example a 404 that means "not found", not "unsupported").
        return api_error(op, status, body_excerpt(op, response.safe_text.strip()), http_status=status, details=response.safe_text)
    if status == 401:
        return AuthError(f"{op.api.id}.{op.id}: the device requires authentication and no usable credentials were configured")
    if status == 403:
        return HttpAccessDenied(
            status, body_excerpt(op, response.safe_text.strip()), api=op.api.id, operation=op.id, detail=f"requires {op.access} access"
        )
    if status == 503:
        return HttpUnavailable(status, body_excerpt(op, response.safe_text.strip()), api=op.api.id, operation=op.id)
    if status == 404:
        return NotSupported(op.api.id, op.id, f"{response.request.path} not found (HTTP 404)")
    return HttpError(status, body_excerpt(op, response.safe_text.strip()), api=op.api.id, operation=op.id)


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
