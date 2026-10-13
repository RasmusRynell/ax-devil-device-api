"""Per-device facts cached across calls.

Only facts about the device are cached (what it advertises, what discovery
returned, its identity), never per-class decisions.

Every write carries a ``Token`` taken before the I/O that produced the fact.
``clear()`` invalidates every outstanding token, and forgetting one key
invalidates the tokens for that key, so a probe or negotiation that was in
flight when its fact was invalidated cannot put the stale fact back. Checks
and writes happen under one lock (never held across I/O or an ``await``), so
the state is safe to share between threads and tasks.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Any, NamedTuple

from .base import ApiVersion


class Token(NamedTuple):
    generation: int
    key_generation: int


class DeviceState:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._generation = 0
        self._key_generations: dict[str, int] = {}
        self._values: dict[str, Any] = {}

    def token(self, key: str) -> Token:
        """Take before the I/O that will produce the fact for ``key``."""
        with self._lock:
            return Token(self._generation, self._key_generations.get(key, 0))

    def get(self, key: str) -> Any:
        """The cached fact, or ``None``."""
        return self._values.get(key)

    def with_prefix(self, prefix: str) -> dict[str, Any]:
        """Snapshot of every cached fact whose key starts with ``prefix``."""
        with self._lock:
            return {k: v for k, v in self._values.items() if k.startswith(prefix)}

    def set(self, key: str, value: Any, token: Token) -> bool:
        """Store ``value`` unless the fact was invalidated since ``token`` was taken."""
        with self._lock:
            if not self._valid(key, token):
                return False
            self._values[key] = value
            return True

    def set_or_clear(self, key: str, value: Any, token: Token, stale: Callable[[Any, Any], bool]) -> None:
        """Store ``value``; if ``stale(old, value)``, first clear everything (e.g. firmware changed).

        The comparison, the clear and the store are one atomic step.
        """
        with self._lock:
            if not self._valid(key, token):
                return
            old = self._values.get(key)
            if old is not None and stale(old, value):
                self._clear_locked()
            self._values[key] = value

    def forget(self, key: str) -> None:
        """Drop one fact and invalidate outstanding tokens for it."""
        with self._lock:
            self._values.pop(key, None)
            self._key_generations[key] = self._key_generations.get(key, 0) + 1

    def clear(self) -> None:
        """Forget everything, e.g. after a firmware upgrade or reboot."""
        with self._lock:
            self._clear_locked()

    def _valid(self, key: str, token: Token) -> bool:
        return token.generation == self._generation and token.key_generation == self._key_generations.get(key, 0)

    def _clear_locked(self) -> None:
        self._generation += 1
        self._values = {}

    # -- Typed helpers for negotiated versions --------------------------------

    def advertised_versions(self, endpoint: str) -> tuple[ApiVersion, ...] | None:
        return self.get(f"versions:{endpoint}")

    def set_advertised_versions(self, endpoint: str, versions: tuple[ApiVersion, ...], token: Token) -> None:
        self.set(f"versions:{endpoint}", versions, token)

    def versions_token(self, endpoint: str) -> Token:
        return self.token(f"versions:{endpoint}")

    def forget_advertised_versions(self, endpoint: str) -> None:
        self.forget(f"versions:{endpoint}")
