"""Device and AsyncDevice: the entry points of the library.

A ``Device`` is meant to live as long as the application talks to the camera
(seconds for a script, weeks for a service). Creating one does no I/O. It
keeps a connection pool, the verified credential, and cached device facts
(negotiated API versions, discovery results, identity). Those facts are
dropped automatically when the device shows they are stale (it rejects a
negotiated version, an endpoint disappears, or ``identity(refresh=True)``
reports new firmware), and manually with ``refresh()``.

A sync ``Device`` may be shared between threads. An ``AsyncDevice`` may be
shared between tasks of one event loop.
"""

from __future__ import annotations

import asyncio
import threading
from collections.abc import Callable, Iterable
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import Any, TypeVar

import httpx

from . import _protocols  # noqa: F401  (registers protocol bindings)
from ._http.config import (
    Auth,
    BearerToken,
    ConnectionConfig,
    Credentials,
    RequestHook,
    ResponseHook,
    Scheme,
    Verify,
)
from ._http.options import DEFAULT_HEARTBEAT, Heartbeat, RequestOptions, RetryPolicy
from ._http.transport import AsyncTransport, SyncTransport
from ._protocols.base import CallFlow, Model, Operation, flow_for
from ._protocols.state import DeviceState, Token
from ._runtime.capabilities import (
    OPTIONAL_PROBES,
    PROBES,
    PROPERTY_SCOPE_PREFIX,
    Capabilities,
    DeviceIdentity,
    SupportResult,
    decide_support,
    extra_probes,
    identity_flow,
    probe_error,
    probe_is_complete,
)
from ._runtime.driver import Call, run_async, run_sync
from ._runtime.ws import (
    AsyncSession,
    Session,
    SessionLedger,
    SessionSpec,
    connect_session,
    connect_session_async,
)
from ._validate import boolean
from .apis import Apis, AsyncApis
from .apis._base import AsyncApi, SyncApi, build_params
from .errors import ConfigurationError
from .rtsp import MEDIA_PATH, MediaStream, RtspBinding, RtspUrl, build_rtsp_url, rtsp_query

S = TypeVar("S", bound=SyncApi)
A = TypeVar("A", bound=AsyncApi)

_IDENTITY = "identity"


def _make_config(
    host: str,
    credentials: Auth | tuple[str, str] | None,
    options: dict[str, Any],
) -> ConnectionConfig:
    if isinstance(credentials, tuple):
        credentials = Credentials.from_pair(credentials)
    retry = options.pop("retry", None)
    if retry is not None:
        options["retry"] = retry
    return ConnectionConfig(host=host, credentials=credentials, **options)


class _DeviceBase:
    config: ConnectionConfig
    _state: DeviceState

    def _call(self, op: Operation[Any] | None, options: RequestOptions | None, label: str | None = None) -> Call:
        return Call(
            op=op,
            label=("device", label) if label else None,
            timeout=options.timeout if options else None,
            retry=(options.retry if options and options.retry else self.config.retry),
            on_response=self.config.on_response,
        )

    def _store_identity(self, identity: DeviceIdentity, token: Token) -> None:
        # New firmware: every cached fact may be wrong now.
        self._state.set_or_clear(_IDENTITY, identity, token, lambda old, new: old.firmware_version != new.firmware_version)

    def _capabilities(self, values: dict[str, Any], errors: dict[str, str]) -> Capabilities:
        # Cached per-property scope probes (run by earlier supports() calls) belong in the snapshot,
        # so decide_support(api.INFO, capabilities()) agrees with supports(api).
        for key, found in self._state.with_prefix(PROPERTY_SCOPE_PREFIX).items():
            values.setdefault(key, found)
        known: DeviceIdentity | None = self._state.get(_IDENTITY)
        if known is not None and known.firmware_version:
            values.setdefault("firmware", known.firmware_version)
        return Capabilities.from_probes(values, errors)

    def rtsp_url(self, stream: MediaStream | None = None, *, port: int = 554, path: str = MEDIA_PATH, include_credentials: bool = False) -> RtspUrl:
        """RTSP URL of this device for ``stream`` (pure; no I/O). Credentials are added only on request.

        Needs password credentials when ``include_credentials`` is set; the
        RTSP port is separate from the HTTP port and defaults to 554.
        """
        return (stream or MediaStream()).url(
            self.config.host, port=port, path=path, credentials=self._rtsp_credentials(include_credentials)
        )

    def _rtsp_credentials(self, include: bool) -> Credentials | None:
        boolean("include_credentials", include)
        credentials = self.config.credentials
        if include and not isinstance(credentials, Credentials):
            raise ConfigurationError("include_credentials needs a username and password (BearerToken cannot be used for RTSP)")
        return credentials if include and isinstance(credentials, Credentials) else None

    def rtsp_url_for(
        self, op: Operation[RtspBinding], kwargs: dict[str, Any] | None = None, /, *, port: int | None = None, include_credentials: bool = False
    ) -> RtspUrl:
        """RTSP URL of a generated RTSP operation (pure; no I/O). Generated API methods call this.

        ``kwargs`` are the operation's arguments (validated like any other call; ``MISSING`` values count as not set).
        ``port`` overrides the binding's RTSP port.
        """
        params = build_params(op, None, dict(kwargs or {}))
        binding = op.binding
        return build_rtsp_url(
            self.config.host,
            port=binding.port if port is None else port,
            path=binding.path,
            params=rtsp_query(binding, params),
            credentials=self._rtsp_credentials(include_credentials),
        )

    def refresh(self) -> None:
        """Forget all cached device facts, e.g. after a firmware upgrade or reboot."""
        self._state.clear()

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.config.base_url}{self.config.base_path}>"


class Device(_DeviceBase):
    """Blocking client for one device. Use as a context manager, or call ``close()``.

    ``dev.apis.<name>`` gives every generated API; ``dev.api(Cls)`` gives one
    by class. API objects are cached and share the connection and device facts.
    """

    def __init__(
        self,
        host: str,
        *,
        credentials: Credentials | BearerToken | tuple[str, str] | None = None,
        scheme: Scheme = "https",
        port: int | None = None,
        base_path: str = "",
        verify: Verify = True,
        proxy: str | None = None,
        timeout: float = 10.0,
        allow_http: bool = False,
        max_concurrency: int = 4,
        max_streams: int = 2,
        retry: RetryPolicy | None = None,
        on_request: RequestHook | None = None,
        on_response: ResponseHook | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        options = dict(
            scheme=scheme, port=port, base_path=base_path, verify=verify, proxy=proxy, timeout=timeout,
            allow_http=allow_http, max_concurrency=max_concurrency, max_streams=max_streams, retry=retry,
            on_request=on_request, on_response=on_response,
        )
        self._setup(_make_config(host, credentials, options), transport)

    @classmethod
    def from_config(cls, config: ConnectionConfig, *, transport: httpx.BaseTransport | None = None) -> Device:
        device = cls.__new__(cls)
        device._setup(config, transport)
        return device

    def _setup(self, config: ConnectionConfig, transport: httpx.BaseTransport | None) -> None:
        self.config = config
        self._transport = SyncTransport(config, transport=transport)
        self._state = DeviceState()
        self._ledger = SessionLedger()
        self._apis: dict[type[SyncApi], SyncApi] = {}
        self._locks: dict[str, threading.Lock] = {}
        self._locks_guard = threading.Lock()
        self.apis = Apis(self)

    # -- APIs ---------------------------------------------------------------

    def api(self, api_class: type[S]) -> S:
        found = self._apis.get(api_class)
        if found is None:
            found = self._apis.setdefault(api_class, api_class(self))
        return found  # type: ignore[return-value]

    def invoke(self, op: Operation[Any], request: Model | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any) -> Any:
        """Run any operation by its descriptor, e.g. ``dev.invoke(mqtt_client.OPS.get_client_status)``."""
        params = build_params(op, request, kwargs)
        return self._execute(op, flow_for(op, params, self._state), request_options)

    def _execute(
        self, op: Operation[Any] | None, flow: CallFlow[Any], options: RequestOptions | None = None, label: str | None = None
    ) -> Any:
        return run_sync(self._transport, flow, self._call(op, options, label))

    def connect_session(
        self,
        spec: SessionSpec,
        /,
        *,
        request_options: RequestOptions | None = None,
        heartbeat: Heartbeat = DEFAULT_HEARTBEAT,
        use_token: bool = False,
        **options: Any,
    ) -> AbstractContextManager[Session]:
        """Open a WebSocket session (``ws.EVENTS``, ``ws.DATA_HUB`` or a generated spec).

        ``options`` are the spec's connect arguments (``event_filter_list=...``).
        ``use_token=True`` authenticates through ``wssession.cgi`` instead of the handshake.
        The session holds one of the device's stream slots until the ``with`` block ends.
        """
        boolean("use_token", use_token)
        return connect_session(
            self._transport, self._ledger, self._call(None, request_options, spec.api_id), spec, options,
            heartbeat=heartbeat, use_token=use_token,
        )

    # -- Device facts -------------------------------------------------------

    def _lock(self, key: str) -> threading.Lock:
        with self._locks_guard:
            return self._locks.setdefault(key, threading.Lock())

    def _cached(self, key: str, make_flow: Callable[[DeviceState], CallFlow[Any]]) -> Any:
        found = self._state.get(key)
        if found is not None:
            return found
        with self._lock(key):
            found = self._state.get(key)
            if found is not None:
                return found
            token = self._state.token(key)
            value = self._execute(None, make_flow(self._state), label=key)
            if probe_is_complete(value):  # a probe with a malformed entry is not cached: the next call asks again
                self._state.set(key, value, token)
            return value

    def identity(self, *, refresh: bool = False) -> DeviceIdentity:
        """Model, serial number and firmware (cached).

        ``refresh=True`` asks the device again; use it as a health check. If
        the firmware changed, all cached device facts are dropped.
        """
        found: DeviceIdentity | None = self._state.get(_IDENTITY)
        if found is not None and not refresh:
            return found
        with self._lock(_IDENTITY):
            found = self._state.get(_IDENTITY)
            if found is not None and not refresh:
                return found  # another caller fetched it while we waited
            token = self._state.token(_IDENTITY)
            identity = self._execute(None, identity_flow(self._state), label=_IDENTITY)
            self._store_identity(identity, token)
            return identity

    def capabilities(self) -> Capabilities:
        """Run (or reuse) every discovery probe. Failed probes are reported, not raised.

        Optional probes (installed applications) are not run here; ``supports`` runs them when an
        API's discovery needs them, and their cached result is included afterwards.
        """
        return self._collect(())

    def _collect(self, extra: tuple[str, ...], *, firmware: bool = False) -> Capabilities:
        probes = {**PROBES, **{k: OPTIONAL_PROBES[k] for k in extra}}
        values: dict[str, Any] = {}
        errors: dict[str, str] = {}
        if firmware:  # an API with a minimum firmware: the identity is fetched once and cached
            try:
                values["firmware"] = self.identity().firmware_version
            except Exception as error:  # noqa: BLE001 - reported in Capabilities.errors
                errors["identity"] = probe_error(error)
        for key, make_flow in probes.items():
            try:
                values[key] = self._cached(key, make_flow)
            except Exception as error:  # noqa: BLE001 - reported in Capabilities.errors
                errors[key] = probe_error(error)
        for key in OPTIONAL_PROBES.keys() - probes.keys():
            if (found := self._state.get(key)) is not None:
                values[key] = found
        return self._capabilities(values, errors)

    def supports(self, api: type[SyncApi] | SyncApi) -> SupportResult:
        """Whether the device offers ``api``: ``YES``, ``NO``, or ``UNKNOWN`` with the probe errors."""
        return decide_support(api.INFO, self._collect(extra_probes(api.INFO), firmware=bool(api.INFO.requires_firmware)))

    def supports_many(self, apis: Iterable[type[SyncApi] | SyncApi]) -> dict[type[SyncApi] | SyncApi, SupportResult]:
        """``supports`` for several APIs from ONE capability snapshot: a failing probe is run once, not once per API."""
        apis = list(apis)
        caps = self._collect(
            tuple(dict.fromkeys(p for a in apis for p in extra_probes(a.INFO))),
            firmware=any(a.INFO.requires_firmware for a in apis),
        )
        return {a: decide_support(a.INFO, caps) for a in apis}

    # -- Lifecycle ----------------------------------------------------------

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> Device:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()


class AsyncDevice(_DeviceBase):
    """Async client for one device. Use as an async context manager, or call ``aclose()``."""

    def __init__(
        self,
        host: str,
        *,
        credentials: Credentials | BearerToken | tuple[str, str] | None = None,
        scheme: Scheme = "https",
        port: int | None = None,
        base_path: str = "",
        verify: Verify = True,
        proxy: str | None = None,
        timeout: float = 10.0,
        allow_http: bool = False,
        max_concurrency: int = 4,
        max_streams: int = 2,
        retry: RetryPolicy | None = None,
        on_request: RequestHook | None = None,
        on_response: ResponseHook | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        options = dict(
            scheme=scheme, port=port, base_path=base_path, verify=verify, proxy=proxy, timeout=timeout,
            allow_http=allow_http, max_concurrency=max_concurrency, max_streams=max_streams, retry=retry,
            on_request=on_request, on_response=on_response,
        )
        self._setup(_make_config(host, credentials, options), transport)

    @classmethod
    def from_config(cls, config: ConnectionConfig, *, transport: httpx.AsyncBaseTransport | None = None) -> AsyncDevice:
        device = cls.__new__(cls)
        device._setup(config, transport)
        return device

    def _setup(self, config: ConnectionConfig, transport: httpx.AsyncBaseTransport | None) -> None:
        self.config = config
        self._transport = AsyncTransport(config, transport=transport)
        self._state = DeviceState()
        self._ledger = SessionLedger()
        self._apis: dict[type[AsyncApi], AsyncApi] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self.apis = AsyncApis(self)

    def api(self, api_class: type[A]) -> A:
        found = self._apis.get(api_class)
        if found is None:
            found = self._apis.setdefault(api_class, api_class(self))
        return found  # type: ignore[return-value]

    async def invoke(
        self, op: Operation[Any], request: Model | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> Any:
        """Run any operation by its descriptor."""
        params = build_params(op, request, kwargs)
        return await self._execute(op, flow_for(op, params, self._state), request_options)

    async def _execute(
        self, op: Operation[Any] | None, flow: CallFlow[Any], options: RequestOptions | None = None, label: str | None = None
    ) -> Any:
        return await run_async(self._transport, flow, self._call(op, options, label))

    def connect_session(
        self,
        spec: SessionSpec,
        /,
        *,
        request_options: RequestOptions | None = None,
        heartbeat: Heartbeat = DEFAULT_HEARTBEAT,
        use_token: bool = False,
        **options: Any,
    ) -> AbstractAsyncContextManager[AsyncSession]:
        """Open a WebSocket session; use as ``async with dev.connect_session(EVENTS, event_filter_list=...) as s``."""
        boolean("use_token", use_token)
        return connect_session_async(
            self._transport, self._ledger, self._call(None, request_options, spec.api_id), spec, options,
            heartbeat=heartbeat, use_token=use_token,
        )

    def _lock(self, key: str) -> asyncio.Lock:
        return self._locks.setdefault(key, asyncio.Lock())

    async def _cached(self, key: str, make_flow: Callable[[DeviceState], CallFlow[Any]]) -> Any:
        found = self._state.get(key)
        if found is not None:
            return found
        async with self._lock(key):
            found = self._state.get(key)
            if found is not None:
                return found
            token = self._state.token(key)
            value = await self._execute(None, make_flow(self._state), label=key)
            if probe_is_complete(value):  # a probe with a malformed entry is not cached: the next call asks again
                self._state.set(key, value, token)
            return value

    async def identity(self, *, refresh: bool = False) -> DeviceIdentity:
        """Model, serial number and firmware (cached); ``refresh=True`` doubles as a health check."""
        found: DeviceIdentity | None = self._state.get(_IDENTITY)
        if found is not None and not refresh:
            return found
        async with self._lock(_IDENTITY):
            found = self._state.get(_IDENTITY)
            if found is not None and not refresh:
                return found  # another caller fetched it while we waited
            token = self._state.token(_IDENTITY)
            identity = await self._execute(None, identity_flow(self._state), label=_IDENTITY)
            self._store_identity(identity, token)
            return identity

    async def capabilities(self) -> Capabilities:
        """Run (or reuse) every discovery probe, concurrently. Failed probes are reported, not raised.

        Optional probes (installed applications) are not run here; ``supports`` runs them when an
        API's discovery needs them, and their cached result is included afterwards.
        """
        return await self._collect(())

    async def _collect(self, extra: tuple[str, ...], *, firmware: bool = False) -> Capabilities:
        probes = {**PROBES, **{k: OPTIONAL_PROBES[k] for k in extra}}
        keys = list(probes)
        fetched: dict[str, Any] = {}
        failed: dict[str, str] = {}
        if firmware:  # an API with a minimum firmware: the identity is fetched once and cached
            try:
                fetched["firmware"] = (await self.identity()).firmware_version
            except Exception as error:  # noqa: BLE001 - reported in Capabilities.errors
                failed["identity"] = probe_error(error)
        # At most max_concurrency probes at a time: a probe's timeout must start when it can be sent,
        # not while it waits for a request slot behind the others (that would turn into a spurious PoolTimeout).
        gate = asyncio.Semaphore(max(1, self.config.max_concurrency))

        async def bounded(key: str) -> Any:
            async with gate:
                return await self._cached(key, probes[key])

        results = await asyncio.gather(*(bounded(k) for k in keys), return_exceptions=True)
        for result in results:
            if isinstance(result, BaseException) and not isinstance(result, Exception):
                raise result  # cancellation and friends
        values = {**fetched, **{k: r for k, r in zip(keys, results) if not isinstance(r, BaseException)}}
        errors = {**failed, **{k: probe_error(r) for k, r in zip(keys, results) if isinstance(r, Exception)}}
        for key in OPTIONAL_PROBES.keys() - probes.keys():
            if (found := self._state.get(key)) is not None:
                values[key] = found
        return self._capabilities(values, errors)

    async def supports(self, api: type[AsyncApi] | AsyncApi) -> SupportResult:
        """Whether the device offers ``api``: ``YES``, ``NO``, or ``UNKNOWN`` with the probe errors."""
        return decide_support(
            api.INFO, await self._collect(extra_probes(api.INFO), firmware=bool(api.INFO.requires_firmware))
        )

    async def supports_many(
        self, apis: Iterable[type[AsyncApi] | AsyncApi]
    ) -> dict[type[AsyncApi] | AsyncApi, SupportResult]:
        """``supports`` for several APIs from ONE capability snapshot: a failing probe is run once, not once per API."""
        apis = list(apis)
        caps = await self._collect(
            tuple(dict.fromkeys(p for a in apis for p in extra_probes(a.INFO))),
            firmware=any(a.INFO.requires_firmware for a in apis),
        )
        return {a: decide_support(a.INFO, caps) for a in apis}

    async def aclose(self) -> None:
        await self._transport.aclose()

    async def __aenter__(self) -> AsyncDevice:
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.aclose()
