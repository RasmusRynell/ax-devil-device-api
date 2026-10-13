# GENERATED from specs/apis/intercom/intercom-ws.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""WebSocket endpoint of the Intercom service for RPC calls and event notifications.

Docs: https://developer.axis.com/vapix/intercom/intercom-service/
"""

from __future__ import annotations

from contextlib import AbstractAsyncContextManager, AbstractContextManager

from .._http.options import DEFAULT_HEARTBEAT, Heartbeat, RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, Family, ParamDiscovery
from .._runtime.ws import AsyncSession, Session, SessionSpec
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


# ---------------------------------------------------------------------------
# Descriptors

# No shared path: every operation names its own endpoint.

INFO = ApiInfo(
    id="intercom-ws",
    name="Intercom service WebSocket",
    family=Family.WS,
    discovery=(
        ParamDiscovery("Properties.API.Intercom.Intercom", "yes"),
        ParamDiscovery("Properties.API.Intercom.Version", "1.1"),
        ApiDiscovery("intercom-api"),
        ApiDiscovery("intercom-reader"),
    ),
    docs=("https://developer.axis.com/vapix/intercom/intercom-service/",),
)


class OPS:
    pass


class SESSIONS:
    connect = SessionSpec(INFO.id, "/vapix/intercomws")


# ---------------------------------------------------------------------------
# API classes


class IntercomWsApi(SyncApi):
    """Intercom service WebSocket (``intercom-ws``)."""

    INFO = INFO

    def connect(
        self,
        *,
        heartbeat: Heartbeat = DEFAULT_HEARTBEAT,
        use_token: bool = False,
        request_options: RequestOptions | None = None,
    ) -> AbstractContextManager[Session]:
        """Open the Intercom service WebSocket (ws/wss) at /vapix/intercomws.

        The same endpoint issues the Intercom API commands (the methods of /vapix/intercom, for example
        `UpdateConfiguration`, `InjectTag`, `SetUiFeedback`) and initiates event notifications, as Google
        JSON or JSON-RPC 2.0 messages. Subscribe with `axev:subscribe` (style `ttMessage`, `topics` such as
        `Device/Intercom/RFID` and `Device/Intercom/KeyPin`, and `functions` that must include
        `axev:notify`, optionally `axdsapi:SetUiFeedback`); list the events with `axev:getSupported`;
        notifications arrive as `axev:notify` (`params.notifications[]` with `topic`, `timestamp`, `data`).
        Methods and types that are functions use the namespace prefix `axdsapi` (for example
        `axdsapi:UpdateConfiguration`). The session carries the frames unchanged (raw codec): there is no
        Google JSON codec, so messages are not built or decoded for you.

        Use as a context manager (``with`` / ``async with``); it yields the WebSocket session. Access:
        admin.
        """
        return self._device.connect_session(
            SESSIONS.connect, request_options=request_options, heartbeat=heartbeat, use_token=use_token
        )


class AsyncIntercomWsApi(AsyncApi):
    """Intercom service WebSocket (``intercom-ws``)."""

    INFO = INFO

    def connect(
        self,
        *,
        heartbeat: Heartbeat = DEFAULT_HEARTBEAT,
        use_token: bool = False,
        request_options: RequestOptions | None = None,
    ) -> AbstractAsyncContextManager[AsyncSession]:
        """Open the Intercom service WebSocket (ws/wss) at /vapix/intercomws.

        The same endpoint issues the Intercom API commands (the methods of /vapix/intercom, for example
        `UpdateConfiguration`, `InjectTag`, `SetUiFeedback`) and initiates event notifications, as Google
        JSON or JSON-RPC 2.0 messages. Subscribe with `axev:subscribe` (style `ttMessage`, `topics` such as
        `Device/Intercom/RFID` and `Device/Intercom/KeyPin`, and `functions` that must include
        `axev:notify`, optionally `axdsapi:SetUiFeedback`); list the events with `axev:getSupported`;
        notifications arrive as `axev:notify` (`params.notifications[]` with `topic`, `timestamp`, `data`).
        Methods and types that are functions use the namespace prefix `axdsapi` (for example
        `axdsapi:UpdateConfiguration`). The session carries the frames unchanged (raw codec): there is no
        Google JSON codec, so messages are not built or decoded for you.

        Use as a context manager (``with`` / ``async with``); it yields the WebSocket session. Access:
        admin.
        """
        return self._device.connect_session(
            SESSIONS.connect, request_options=request_options, heartbeat=heartbeat, use_token=use_token
        )
