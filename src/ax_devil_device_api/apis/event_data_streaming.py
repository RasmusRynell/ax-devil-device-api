# GENERATED from specs/apis/network-video/event-data-streaming.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Receive ONVIF XML event notifications in the RTSP/RTP metadata stream (/axis-media/media.amp?event=on&eventtopic=...&eventcontent=...).

Docs: https://developer.axis.com/vapix/network-video/event-data-streaming/
"""

from __future__ import annotations

from typing import Literal

from pydantic import MISSING

from .._protocols.base import ApiInfo, Family, Model, Operation, ParamDiscovery
from ..rtsp import RtspBinding, RtspUrl
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class SubscribeEventStreamUrlRequest(Model):
    video: Literal[0, 1] | None = None
    """0 = no video, 1 = video. Default: 1."""
    audio: Literal[0, 1] | None = None
    """0 = no audio, 1 = audio. Default: 1."""
    eventtopic: str | None = None
    """Comma-separated list of event topic filters (ONVIF ConcreteSet dialect, using filter namespaces onvif/axis instead of tns1/tnsaxis). An empty string, the default, includes all events."""
    eventcontent: str | None = None
    """Event content filter (ONVIF ItemFilter dialect), e.g. boolean(//SimpleItem[@Name="port" and @Value="1"]). Spaces and special characters (incl. quotes) are percent-encoded in the URL."""


# ---------------------------------------------------------------------------
# Descriptors

# No shared path: every operation names its own endpoint.

INFO = ApiInfo(
    id="event-data-streaming",
    name="Event data streaming",
    family=Family.RTSP,
    discovery=(
        ParamDiscovery("Properties.API.Metadata.Metadata", "yes"),
        ParamDiscovery("Properties.API.Metadata.Version", "1.00"),
    ),
    requires_firmware="5.50",
    docs=("https://developer.axis.com/vapix/network-video/event-data-streaming/",),
)


class OPS:
    subscribe_event_stream_url = Operation(
        INFO,
        "subscribe_event_stream_url",
        RtspBinding(fixed_query=(("event", "on"),)),
        params=SubscribeEventStreamUrlRequest,
        access="admin",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class EventDataStreamingApi(SyncApi):
    """Event data streaming (``event-data-streaming``)."""

    INFO = INFO

    def subscribe_event_stream_url(
        self,
        *,
        video: Literal[0, 1] | MISSING = MISSING,
        audio: Literal[0, 1] | MISSING = MISSING,
        eventtopic: str | MISSING = MISSING,
        eventcontent: str | MISSING = MISSING,
        port: int | None = None,
        include_credentials: bool = False,
    ) -> RtspUrl:
        """Build the RTSP URL that subscribes to the event stream (same syntax as video/audio streams plus event arguments).

        Returns an RTSP URL with event=on; open it with an RTSP client and parse the ONVIF XML notifications
        in the metadata stream. Only subscribe to events of interest; subscriptions start internal services
        and may cause performance problems. On connect, all stateful events send a notification with their
        current state. The eventtopic and eventcontent filters use the filter namespaces onvif/axis, not the
        declaration namespaces tns1/tnsaxis; several ConcreteSet topic paths may be joined with "|" in one
        filter or given as a comma-separated list. Special characters in eventcontent (spaces, quotation
        marks) are percent-encoded when the URL is built, so pass the expression unencoded. For further
        arguments (videocodec, resolution, ...) see the Video streaming over RTSP API.

        Builds the URL only; no request is made. Access: admin.
        """
        return self._device.rtsp_url_for(
            OPS.subscribe_event_stream_url,
            {"video": video, "audio": audio, "eventtopic": eventtopic, "eventcontent": eventcontent},
            port=port,
            include_credentials=include_credentials,
        )


class AsyncEventDataStreamingApi(AsyncApi):
    """Event data streaming (``event-data-streaming``)."""

    INFO = INFO

    def subscribe_event_stream_url(
        self,
        *,
        video: Literal[0, 1] | MISSING = MISSING,
        audio: Literal[0, 1] | MISSING = MISSING,
        eventtopic: str | MISSING = MISSING,
        eventcontent: str | MISSING = MISSING,
        port: int | None = None,
        include_credentials: bool = False,
    ) -> RtspUrl:
        """Build the RTSP URL that subscribes to the event stream (same syntax as video/audio streams plus event arguments).

        Returns an RTSP URL with event=on; open it with an RTSP client and parse the ONVIF XML notifications
        in the metadata stream. Only subscribe to events of interest; subscriptions start internal services
        and may cause performance problems. On connect, all stateful events send a notification with their
        current state. The eventtopic and eventcontent filters use the filter namespaces onvif/axis, not the
        declaration namespaces tns1/tnsaxis; several ConcreteSet topic paths may be joined with "|" in one
        filter or given as a comma-separated list. Special characters in eventcontent (spaces, quotation
        marks) are percent-encoded when the URL is built, so pass the expression unencoded. For further
        arguments (videocodec, resolution, ...) see the Video streaming over RTSP API.

        Builds the URL only; no request is made. Access: admin.
        """
        return self._device.rtsp_url_for(
            OPS.subscribe_event_stream_url,
            {"video": video, "audio": audio, "eventtopic": eventtopic, "eventcontent": eventcontent},
            port=port,
            include_credentials=include_credentials,
        )
