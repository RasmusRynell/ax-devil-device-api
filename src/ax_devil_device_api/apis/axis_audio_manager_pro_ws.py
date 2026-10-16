# GENERATED from specs/apis/audio-systems/axis-audio-manager-pro-ws.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Send and receive binary audio of an Audio Manager Pro audio session over a WebSocket.

Docs: https://developer.axis.com/vapix/audio-systems/axis-audio-manager-pro-api/
"""

from __future__ import annotations

from contextlib import AbstractAsyncContextManager, AbstractContextManager

from pydantic import Field

from .._http.options import DEFAULT_HEARTBEAT, Heartbeat, RequestOptions
from .._protocols.base import ApiInfo, Family, Model
from .._runtime.ws import AsyncSession, Session, SessionSpec
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class ReceiveAudioRequest(Model):
    audio_session_id: str = Field(validation_alias="audioSessionId", serialization_alias="audioSessionId")
    """The ID of the WebSocket audio session."""


class SendAudioRequest(Model):
    audio_session_id: str = Field(validation_alias="audioSessionId", serialization_alias="audioSessionId")
    """The ID of the WebSocket audio session."""


class SendReceiveAudioRequest(Model):
    audio_session_id: str = Field(validation_alias="audioSessionId", serialization_alias="audioSessionId")
    """The ID of the WebSocket audio session."""


# ---------------------------------------------------------------------------
# Descriptors

# No shared path: every operation names its own endpoint.

INFO = ApiInfo(
    id="axis-audio-manager-pro-ws",
    name="AXIS Audio Manager Pro WebSocket audio",
    family=Family.WS,
    requires_application="AXIS Audio Manager Pro (server software)",
    docs=("https://developer.axis.com/vapix/audio-systems/axis-audio-manager-pro-api/",),
)


class OPS:
    pass


class SESSIONS:
    receive_audio = SessionSpec(INFO.id, "/api/v1.2/audioSessions/{audioSessionId}/ws/recv")
    send_audio = SessionSpec(INFO.id, "/api/v1.2/audioSessions/{audioSessionId}/ws/send")
    send_receive_audio = SessionSpec(INFO.id, "/api/v1.2/audioSessions/{audioSessionId}/ws/sendrecv")


# ---------------------------------------------------------------------------
# API classes


class AxisAudioManagerProWsApi(SyncApi):
    """AXIS Audio Manager Pro WebSocket audio (``axis-audio-manager-pro-ws``)."""

    INFO = INFO

    def receive_audio(
        self,
        audio_session_id: str,
        *,
        heartbeat: Heartbeat = DEFAULT_HEARTBEAT,
        use_token: bool = False,
        request_options: RequestOptions | None = None,
    ) -> AbstractContextManager[Session]:
        """Open a WebSocket that receives binary audio from a WS audio session.

        Audio is only transmitted over this connection if a duplex device is configured within the audio
        session. The frames are binary audio; the session passes them through unchanged (`bytes`). The audio
        session is a WS audio session created with the audio sessions REST API.

        Use as a context manager (``with`` / ``async with``); it yields the WebSocket session. Access:
        admin.
        """
        return self._device.connect_session(
            SESSIONS.receive_audio.bind({"audioSessionId": audio_session_id}),
            request_options=request_options,
            heartbeat=heartbeat,
            use_token=use_token,
        )

    def send_audio(
        self,
        audio_session_id: str,
        *,
        heartbeat: Heartbeat = DEFAULT_HEARTBEAT,
        use_token: bool = False,
        request_options: RequestOptions | None = None,
    ) -> AbstractContextManager[Session]:
        """Open a WebSocket that sends binary audio to a WS audio session.

        The audio stream must be sent in binary format (binary frames).

        Use as a context manager (``with`` / ``async with``); it yields the WebSocket session. Access:
        admin.
        """
        return self._device.connect_session(
            SESSIONS.send_audio.bind({"audioSessionId": audio_session_id}),
            request_options=request_options,
            heartbeat=heartbeat,
            use_token=use_token,
        )

    def send_receive_audio(
        self,
        audio_session_id: str,
        *,
        heartbeat: Heartbeat = DEFAULT_HEARTBEAT,
        use_token: bool = False,
        request_options: RequestOptions | None = None,
    ) -> AbstractContextManager[Session]:
        """Open a bidirectional WebSocket that sends and receives binary audio of a WS audio session.

        Audio in both directions is binary frames.

        Use as a context manager (``with`` / ``async with``); it yields the WebSocket session. Access:
        admin.
        """
        return self._device.connect_session(
            SESSIONS.send_receive_audio.bind({"audioSessionId": audio_session_id}),
            request_options=request_options,
            heartbeat=heartbeat,
            use_token=use_token,
        )


class AsyncAxisAudioManagerProWsApi(AsyncApi):
    """AXIS Audio Manager Pro WebSocket audio (``axis-audio-manager-pro-ws``)."""

    INFO = INFO

    def receive_audio(
        self,
        audio_session_id: str,
        *,
        heartbeat: Heartbeat = DEFAULT_HEARTBEAT,
        use_token: bool = False,
        request_options: RequestOptions | None = None,
    ) -> AbstractAsyncContextManager[AsyncSession]:
        """Open a WebSocket that receives binary audio from a WS audio session.

        Audio is only transmitted over this connection if a duplex device is configured within the audio
        session. The frames are binary audio; the session passes them through unchanged (`bytes`). The audio
        session is a WS audio session created with the audio sessions REST API.

        Use as a context manager (``with`` / ``async with``); it yields the WebSocket session. Access:
        admin.
        """
        return self._device.connect_session(
            SESSIONS.receive_audio.bind({"audioSessionId": audio_session_id}),
            request_options=request_options,
            heartbeat=heartbeat,
            use_token=use_token,
        )

    def send_audio(
        self,
        audio_session_id: str,
        *,
        heartbeat: Heartbeat = DEFAULT_HEARTBEAT,
        use_token: bool = False,
        request_options: RequestOptions | None = None,
    ) -> AbstractAsyncContextManager[AsyncSession]:
        """Open a WebSocket that sends binary audio to a WS audio session.

        The audio stream must be sent in binary format (binary frames).

        Use as a context manager (``with`` / ``async with``); it yields the WebSocket session. Access:
        admin.
        """
        return self._device.connect_session(
            SESSIONS.send_audio.bind({"audioSessionId": audio_session_id}),
            request_options=request_options,
            heartbeat=heartbeat,
            use_token=use_token,
        )

    def send_receive_audio(
        self,
        audio_session_id: str,
        *,
        heartbeat: Heartbeat = DEFAULT_HEARTBEAT,
        use_token: bool = False,
        request_options: RequestOptions | None = None,
    ) -> AbstractAsyncContextManager[AsyncSession]:
        """Open a bidirectional WebSocket that sends and receives binary audio of a WS audio session.

        Audio in both directions is binary frames.

        Use as a context manager (``with`` / ``async with``); it yields the WebSocket session. Access:
        admin.
        """
        return self._device.connect_session(
            SESSIONS.send_receive_audio.bind({"audioSessionId": audio_session_id}),
            request_options=request_options,
            heartbeat=heartbeat,
            use_token=use_token,
        )
