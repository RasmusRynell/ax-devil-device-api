"""Per-device retry policy and per-call request options."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .._validate import (
    boolean,
    bounded_int,
    non_negative_finite,
    optional_positive_finite,
    positive_finite,
    positive_int,
)
from ..errors import ConfigurationError


def require_int(name: str, value: Any, minimum: int) -> None:
    """Kept for existing callers: ``bounded_int(name, value, minimum)``."""
    bounded_int(name, value, minimum)


@dataclass(frozen=True)
class RetryPolicy:
    """When the library resends a request after a transport failure.

    - Requests that provably never reached the device (``TransportError.request_sent``
      is ``False``: connection refused, connect timeout, no free connection) are
      retried for every operation, because the device cannot have acted on them.
    - With ``retry_reads=True``, operations whose effect is ``read`` are also
      retried after failures where the request may have been sent (read
      timeout, dropped connection), if the body can be resent.
    - Writes and actions are never resent after the request may have arrived.
    - HTTP and API errors are never retried.
    """

    attempts: int = 2
    """Total attempts, including the first."""
    retry_unsent: bool = True
    retry_reads: bool = False
    backoff: float = 0.2
    """Delay before the first retry, in seconds; doubles each retry."""
    max_backoff: float = 5.0

    def __post_init__(self) -> None:
        positive_int("attempts", self.attempts)
        boolean("retry_unsent", self.retry_unsent)
        boolean("retry_reads", self.retry_reads)
        non_negative_finite("backoff", self.backoff)
        non_negative_finite("max_backoff", self.max_backoff)

    def delay(self, retry_number: int) -> float:
        """Delay before retry ``retry_number`` (1 = first retry)."""
        return min(self.backoff * (2.0 ** min(retry_number - 1, 1000)), self.max_backoff)


NO_RETRY = RetryPolicy(attempts=1)


@dataclass(frozen=True)
class RequestOptions:
    """Overrides for one call: ``api.method(..., request_options=RequestOptions(timeout=120))``."""

    timeout: float | None = None
    """Seconds; replaces the device and operation timeout for every request of the call."""
    retry: RetryPolicy | None = None
    """Replaces the device retry policy for this call."""

    def __post_init__(self) -> None:
        if self.retry is not None and not isinstance(self.retry, RetryPolicy):
            raise ConfigurationError(f"retry must be a RetryPolicy or None, got {self.retry!r}")
        optional_positive_finite(
            "timeout", self.timeout, "; use None to keep the device timeout (there is no way to disable timeouts)"
        )


@dataclass(frozen=True)
class Heartbeat:
    """Liveness checking for a WebSocket session.

    The device documents no application-level heartbeat, so liveness uses
    WebSocket ping frames: every ``interval`` seconds the client pings; if no
    pong arrives within ``timeout`` the session ends with ``ConnectionFailed``
    (and is reported as an abnormal end, see ``Gap``). ``Heartbeat(None)``
    disables pings, and a silent half-open connection is then never noticed.
    Idle event streams are normal, so silence alone never ends a session.
    """

    interval: float | None = 20.0
    timeout: float = 20.0

    def __post_init__(self) -> None:
        optional_positive_finite("interval", self.interval, " (use Heartbeat(None) to disable pings)")
        positive_finite("timeout", self.timeout)


DEFAULT_HEARTBEAT = Heartbeat()
NO_HEARTBEAT = Heartbeat(None)
