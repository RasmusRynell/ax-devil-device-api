"""Per-device retry policy and per-call request options."""

from __future__ import annotations

import math
from dataclasses import dataclass


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
        if self.attempts < 1:
            raise ValueError("attempts must be at least 1")
        if not self.backoff >= 0:
            raise ValueError("backoff must not be negative")
        if not self.max_backoff >= 0:
            raise ValueError("max_backoff must not be negative")

    def delay(self, retry_number: int) -> float:
        """Delay before retry ``retry_number`` (1 = first retry)."""
        return min(self.backoff * (2 ** (retry_number - 1)), self.max_backoff)


NO_RETRY = RetryPolicy(attempts=1)


@dataclass(frozen=True)
class RequestOptions:
    """Overrides for one call: ``api.method(..., request_options=RequestOptions(timeout=120))``."""

    timeout: float | None = None
    """Seconds; replaces the device and operation timeout for every request of the call."""
    retry: RetryPolicy | None = None
    """Replaces the device retry policy for this call."""

    def __post_init__(self) -> None:
        if self.timeout is not None and not (isinstance(self.timeout, (int, float)) and 0 < self.timeout < math.inf):
            raise ValueError(
                f"timeout must be a positive, finite number of seconds, got {self.timeout!r}; "
                "use None to keep the device timeout (there is no way to disable timeouts)"
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
        if self.interval is not None and not 0 < self.interval < math.inf:
            raise ValueError("interval must be positive and finite (use Heartbeat(None) to disable pings)")
        if not 0 < self.timeout < math.inf:
            raise ValueError("timeout must be positive and finite")


DEFAULT_HEARTBEAT = Heartbeat()
NO_HEARTBEAT = Heartbeat(None)
