"""Challenge-driven authentication for Axis devices (Basic and Digest).

``AxisAuth`` keeps the auth state of one device. Each request gets its own
``httpx.Auth`` from ``for_request``; the flow is a plain generator, so the same
code serves ``httpx.Client`` and ``httpx.AsyncClient``.

Credentials are only sent after the device has challenged, or pre-emptively
once a credential has been *verified* by an authenticated 2xx response. A
credential built from a challenge (a *candidate*) is never reused until then.
"""

from __future__ import annotations

import base64
import hashlib
import os
import re
import threading
from collections.abc import Generator
from dataclasses import dataclass

import httpx

from ..errors import AuthError
from .config import BearerToken, Credentials
from .types import AuthPolicy

# --------------------------------------------------------------------------
# Challenge parsing

_TOKEN_RE = re.compile(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+")


@dataclass(frozen=True)
class Challenge:
    """One parsed ``WWW-Authenticate`` challenge; parameter names are lower-case."""

    scheme: str
    params: dict[str, str]


def parse_challenges(values: list[str]) -> list[Challenge]:
    """Parse every challenge from the given ``WWW-Authenticate`` header values.

    Handles several challenges in one header and quoted strings containing
    commas. A malformed header (unterminated quote) yields no challenges.
    """
    result: list[Challenge] = []
    for value in values:
        parsed = _parse_header(value)
        if parsed is None:
            continue
        result.extend(parsed)
    return result


def _skip(value: str, i: int, chars: str) -> int:
    while i < len(value) and value[i] in chars:
        i += 1
    return i


def _parse_header(value: str) -> list[Challenge] | None:
    n = len(value)
    challenges: list[Challenge] = []
    i = 0
    while True:
        i = _skip(value, i, " \t,")
        match = _TOKEN_RE.match(value, i)
        if match is None:
            return challenges if i >= n else None
        scheme = match.group()
        i = match.end()
        params: dict[str, str] = {}
        while True:
            j = _skip(value, i, " \t,")
            name = _TOKEN_RE.match(value, j)
            if name is None:
                i = j
                break
            k = _skip(value, name.end(), " \t")
            if k >= n or value[k] != "=":
                i = j  # next scheme begins here
                break
            k = _skip(value, k + 1, " \t")
            if k < n and value[k] == '"':
                k += 1
                chars: list[str] = []
                while k < n and value[k] != '"':
                    if value[k] == "\\" and k + 1 < n:
                        k += 1
                    chars.append(value[k])
                    k += 1
                if k >= n:
                    return None  # unterminated quote
                k += 1
                params[name.group().lower()] = "".join(chars)
            else:
                end = k
                while end < n and value[end] not in ", \t":
                    end += 1
                params[name.group().lower()] = value[k:end]
                k = end
            i = k
        challenges.append(Challenge(scheme.lower(), params))


# --------------------------------------------------------------------------
# Digest

_HASHES: dict[str, str] = {
    "MD5": "md5",
    "SHA": "sha1",
    "SHA-256": "sha256",
    "SHA-512": "sha512",
    "SHA-512-256": "sha512_256",
}


@dataclass(frozen=True)
class DigestChallenge:
    """A validated Digest challenge."""

    realm: str
    nonce: str
    opaque: str | None
    algorithm: str  # as advertised, upper-case
    qop_auth: bool
    stale: bool

    @property
    def hash_name(self) -> str:
        return _HASHES[self.algorithm.removesuffix("-SESS")]

    @property
    def sess(self) -> bool:
        return self.algorithm.endswith("-SESS")


def parse_digest(challenge: Challenge) -> DigestChallenge:
    """Validate a Digest challenge, raising ``AuthError`` if unsupported."""
    params = challenge.params
    realm, nonce = params.get("realm"), params.get("nonce")
    if not realm or not nonce:
        raise AuthError("authentication failed: Digest challenge lacks a valid realm and nonce")
    algorithm = params.get("algorithm", "MD5").upper()
    base = algorithm.removesuffix("-SESS")
    if base not in _HASHES:
        raise AuthError(f"authentication failed: unsupported Digest algorithm {algorithm!r}")
    try:
        hashlib.new(_HASHES[base])
    except ValueError as error:
        raise AuthError(f"authentication failed: Digest algorithm {algorithm!r} unavailable") from error
    qop = params.get("qop")
    qop_auth = False
    if qop is not None:
        if "auth" not in {q.strip().lower() for q in qop.split(",")}:
            raise AuthError("authentication failed: unsupported Digest quality of protection")
        qop_auth = True
    return DigestChallenge(
        realm=realm,
        nonce=nonce,
        opaque=params.get("opaque"),
        algorithm=algorithm,
        qop_auth=qop_auth,
        stale=params.get("stale", "").lower() == "true",
    )


def _quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


class _Counter:
    """Thread-safe nonce counter for one Digest challenge."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._value = 0

    def next(self) -> int:
        with self._lock:
            self._value += 1
            return self._value


@dataclass(frozen=True)
class _DigestState:
    challenge: DigestChallenge
    counter: _Counter

    def header(self, credentials: Credentials, method: str, uri: str) -> str:
        ch = self.challenge

        def h(text: str) -> str:
            return hashlib.new(ch.hash_name, text.encode("utf-8")).hexdigest()

        cnonce = os.urandom(8).hex()
        ha1 = h(f"{credentials.username}:{ch.realm}:{credentials.password}")
        if ch.sess:
            ha1 = h(f"{ha1}:{ch.nonce}:{cnonce}")
        ha2 = h(f"{method}:{uri}")
        nc = f"{self.counter.next():08x}"
        if ch.qop_auth:
            response = h(f"{ha1}:{ch.nonce}:{nc}:{cnonce}:auth:{ha2}")
        else:
            response = h(f"{ha1}:{ch.nonce}:{ha2}")
        parts = [
            f"username={_quote(credentials.username)}",
            f"realm={_quote(ch.realm)}",
            f"nonce={_quote(ch.nonce)}",
            f"uri={_quote(uri)}",
            f"response={_quote(response)}",
        ]
        parts.append(f"algorithm={ch.algorithm}")
        if ch.opaque is not None:
            parts.append(f"opaque={_quote(ch.opaque)}")
        if ch.qop_auth:
            parts += ["qop=auth", f"nc={nc}", f"cnonce={_quote(cnonce)}"]
        elif ch.sess:
            parts.append(f"cnonce={_quote(cnonce)}")
        return "Digest " + ", ".join(parts)


@dataclass(frozen=True)
class _BasicState:
    def header(self, credentials: Credentials, method: str, uri: str) -> str:
        raw = f"{credentials.username}:{credentials.password}".encode()
        return "Basic " + base64.b64encode(raw).decode("ascii")


_State = _DigestState | _BasicState


def _state_from_challenges(response: httpx.Response) -> _State:
    """Pick the best supported challenge (Digest over Basic) and build a state."""
    challenges = parse_challenges(response.headers.get_list("www-authenticate"))
    digests = [c for c in challenges if c.scheme == "digest"]
    if digests:
        error: AuthError | None = None
        for challenge in digests:
            try:
                return _DigestState(parse_digest(challenge), _Counter())
            except AuthError as exc:
                error = exc
        assert error is not None
        raise error
    if any(c.scheme == "basic" for c in challenges):
        return _BasicState()
    raise AuthError("authentication failed: HTTP 401 without a supported Basic or Digest challenge")


# --------------------------------------------------------------------------
# Auth object

_REPLAY_MESSAGE = (
    "request body cannot be replayed after an authentication challenge; "
    "re-supply the body or authenticate first with a replayable request"
)


class AxisAuth:
    """Authentication state for one device."""

    def __init__(self, credentials: Credentials | BearerToken | None) -> None:
        self._credentials = credentials
        self._verified: _State | None = None  # replaced under _lock, never mutated
        self._lock = threading.Lock()

    def _promote(self, state: _State) -> None:
        with self._lock:
            self._verified = state

    def _demote(self, expected: _State) -> None:
        """Forget ``expected``, unless another request already replaced it."""
        with self._lock:
            if self._verified is expected:
                self._verified = None

    @property
    def has_verified_state(self) -> bool:
        return self._verified is not None

    @property
    def uses_password(self) -> bool:
        """Whether requests are signed with a password (Digest/Basic), as opposed to a token or nothing."""
        return isinstance(self._credentials, Credentials)

    @property
    def needs_verification(self) -> bool:
        """Whether a one-shot body would fail now: password credentials with no verified state."""
        return isinstance(self._credentials, Credentials) and self._verified is None

    def reset(self) -> None:
        """Forget any verified credential."""
        with self._lock:
            self._verified = None

    def for_request(self, policy: AuthPolicy, replayable: bool) -> httpx.Auth:
        """Return the ``httpx.Auth`` to use for one request."""
        return _Flow(self, policy, replayable)


def _is_stale(response: httpx.Response) -> bool:
    """Whether a 401 only reports an expired Digest nonce (``stale=true``)."""
    return any(
        c.scheme == "digest" and c.params.get("stale", "").lower() == "true"
        for c in parse_challenges(response.headers.get_list("www-authenticate"))
    )


class _Flow(httpx.Auth):
    """Per-request auth flow bound to an ``AxisAuth``."""

    def __init__(self, owner: AxisAuth, policy: AuthPolicy, replayable: bool) -> None:
        self._owner = owner
        self._policy = policy
        self._replayable = replayable
        self.requires_request_body = replayable

    def _bearer_flow(
        self, token: BearerToken, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        if self._policy == "if_challenged" and self._replayable:
            # Never pre-emptive: probe anonymously and send the token only if the device asks for credentials.
            response = yield request
            if response.status_code != 401 or not response.headers.get_list("www-authenticate"):
                return
        request.headers["Authorization"] = f"Bearer {token.current()}"
        response = yield request
        if response.status_code != 401:
            return
        if callable(token.token) and self._replayable:
            request.headers["Authorization"] = f"Bearer {token.current()}"
            response = yield request
            if response.status_code != 401:
                return
        raise AuthError("authentication failed: the device rejected the bearer token")

    def _sign(self, state: _State, request: httpx.Request) -> None:
        credentials = self._owner._credentials
        if not isinstance(credentials, Credentials):  # not an assert: those vanish under -O
            raise AuthError("authentication failed: a username and password are needed for this challenge")
        uri = request.url.raw_path.decode("ascii")
        request.headers["Authorization"] = state.header(credentials, request.method, uri)

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        owner = self._owner
        if self._policy == "anonymous" or owner._credentials is None:
            yield request
            return
        if isinstance(owner._credentials, BearerToken):
            yield from self._bearer_flow(owner._credentials, request)
            return

        verified = owner._verified if self._policy == "required" else None
        if verified is not None:
            self._sign(verified, request)
            response = yield request
            if response.status_code != 401:
                return
            if not _is_stale(response):
                # A stale nonce only needs refreshing: keep the verified state until its replacement is promoted,
                # so a concurrent one-shot upload is not left without credentials.
                owner._demote(verified)
            if not self._replayable:
                raise AuthError(
                    "authentication failed: the device rejected the stored credentials, and the request "
                    "body cannot be replayed to retry"
                )
            request.headers.pop("Authorization", None)
        else:
            if not self._replayable:
                error = AuthError(_REPLAY_MESSAGE)
                error.body_untouched = True  # type: ignore[attr-defined]  # raised before anything was sent
                raise error
            response = yield request
            if response.status_code != 401:
                return

        if self._policy == "if_challenged" and not response.headers.get_list("www-authenticate"):
            # A 401 that offers no challenge (pwdgrp.cgi before the first administrator exists) is an
            # answer of the API, not a request for credentials: hand it to the protocol layer.
            return
        for attempt in range(2):
            candidate = _state_from_challenges(response)
            self._sign(candidate, request)
            response = yield request
            # 101 Switching Protocols is the success of an authenticated WebSocket upgrade.
            if 200 <= response.status_code < 300 or response.status_code == 101:
                owner._promote(candidate)
                return
            if response.status_code != 401:
                return
            stale = isinstance(candidate, _DigestState) and _is_stale(response)
            if not stale or attempt == 1:
                break
            request.headers.pop("Authorization", None)
        owner._demote(verified) if verified is not None else None
        raise AuthError("authentication failed: the device rejected the credentials")


__all__ = ["AxisAuth", "Challenge", "DigestChallenge", "parse_challenges", "parse_digest"]
