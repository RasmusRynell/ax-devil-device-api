"""Validators for public numeric inputs.

Every check rejects ``bool`` (``True`` is an ``int`` in Python but never a count or a duration), accepts only real
``int`` for counts and real numbers for durations, and raises ``ConfigurationError`` (a ``ValueError``) naming the
setting and the offending value.
"""

from __future__ import annotations

import math
from typing import Any

from .errors import ConfigurationError


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def bounded_int(name: str, value: Any, lo: int | None = None, hi: int | None = None) -> int:
    """``value`` as an ``int`` within ``lo``..``hi`` (either bound optional)."""
    if not _is_int(value) or (lo is not None and value < lo) or (hi is not None and value > hi):
        if lo is not None and hi is not None:
            expected = f"an integer between {lo} and {hi}"
        elif lo is not None:
            expected = f"an integer of at least {lo}"
        else:
            expected = "an integer"
        raise ConfigurationError(f"{name} must be {expected}, got {value!r}")
    return value


def positive_int(name: str, value: Any) -> int:
    return bounded_int(name, value, 1)


def non_negative_int(name: str, value: Any) -> int:
    return bounded_int(name, value, 0)


def positive_finite(name: str, value: Any, hint: str = "") -> float:
    if not _is_number(value) or not 0 < value < math.inf:
        raise ConfigurationError(f"{name} must be a positive, finite number, got {value!r}{hint}")
    return value


def non_negative_finite(name: str, value: Any) -> float:
    if not _is_number(value) or not 0 <= value < math.inf:
        raise ConfigurationError(f"{name} must be finite and not negative, got {value!r}")
    return value


def text(name: str, value: Any, *, allow_empty: bool = False) -> str:
    """``value`` as a real ``str`` (never ``None``, ``bytes`` or a number); empty only with ``allow_empty``."""
    if not isinstance(value, str) or (not value and not allow_empty):
        # Names the type only: this validates credentials, and a secret must not end up in an error message.
        raise ConfigurationError(f"{name} must be {'a' if allow_empty else 'a non-empty'} string, got {type(value).__name__}")
    return value


def header_safe_secret(name: str, value: str, *, inner_space: bool = False, ascii_only: bool = False) -> str:
    """``value`` unchanged if it has no control character or stray whitespace, else a ``ConfigurationError``.

    Leading and trailing whitespace is always refused (a secret read from a file keeps its newline or a space); so is
    whitespace inside the value unless ``inner_space`` (a password may contain spaces, a token or user name may not).

    Credentials end up in headers. A trailing newline (typical when a secret is read from a file) would make httpx
    reject the request in transit, so it is reported where the value is used, never stripped silently (that would
    change a credential). The message names the setting, never the value.
    """
    if any(ord(c) < 32 or 127 <= ord(c) < 160 for c in value):
        raise ConfigurationError(f"{name} contains a newline or other control character (strip it when reading it from a file)")
    if value != value.strip():
        raise ConfigurationError(f"{name} has leading or trailing whitespace (strip it when reading it from a file)")
    if not inner_space and any(c.isspace() for c in value):
        raise ConfigurationError(f"{name} contains whitespace")
    if ascii_only and not value.isascii():
        raise ConfigurationError(f"{name} must contain only ASCII characters")
    return value


def boolean(name: str, value: Any) -> bool:
    if not isinstance(value, bool):
        raise ConfigurationError(f"{name} must be True or False, got {value!r}")
    return value


def optional_bounded_int(name: str, value: Any, lo: int | None = None, hi: int | None = None) -> int | None:
    return None if value is None else bounded_int(name, value, lo, hi)


def optional_positive_int(name: str, value: Any) -> int | None:
    return None if value is None else positive_int(name, value)


def optional_non_negative_int(name: str, value: Any) -> int | None:
    return None if value is None else non_negative_int(name, value)


def optional_positive_finite(name: str, value: Any, hint: str = "") -> float | None:
    return None if value is None else positive_finite(name, value, hint)


def optional_non_negative_finite(name: str, value: Any) -> float | None:
    return None if value is None else non_negative_finite(name, value)
