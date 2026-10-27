# GENERATED from specs/apis/network-video/open-casing-faulty-front-window.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Two events: casing opened (tns1:Device/tnsaxis:Casing/Open) and faulty front window (tns1:Device/tnsaxis:Window/Faulty).

Docs: https://developer.axis.com/vapix/network-video/open-casing-faulty-front-window/
"""

from __future__ import annotations

from .._protocols.base import ApiInfo, Family, Operation
from ..rtsp import RtspBinding, RtspUrl
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


# ---------------------------------------------------------------------------
# Descriptors

# No shared path: every operation names its own endpoint.

INFO = ApiInfo(
    id="open-casing-faulty-front-window",
    name="Open Casing and Faulty Front Window",
    family=Family.RTSP,
    docs=("https://developer.axis.com/vapix/network-video/open-casing-faulty-front-window/",),
)


class OPS:
    stream_casing_events_url = Operation(
        INFO,
        "stream_casing_events_url",
        RtspBinding(fixed_query=(("event", "on"), ("eventtopic", "tns1:Device/Casing"))),
        access="admin",
        effect="read",
    )
    stream_window_events_url = Operation(
        INFO,
        "stream_window_events_url",
        RtspBinding(fixed_query=(("event", "on"), ("eventtopic", "tns1:Device/Window"))),
        access="admin",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class OpenCasingFaultyFrontWindowApi(SyncApi):
    """Open Casing and Faulty Front Window (``open-casing-faulty-front-window``)."""

    INFO = INFO

    def stream_casing_events_url(self, *, port: int | None = None, include_credentials: bool = False) -> RtspUrl:
        """Build the RTSP URL of the event stream for the open casing topic.

        Open it with an RTSP client to receive the casing events (declared as
        tns1:Device/tnsaxis:Casing/Open).

        Builds the URL only; no request is made. Access: admin.
        """
        return self._device.rtsp_url_for(
            OPS.stream_casing_events_url, {}, port=port, include_credentials=include_credentials
        )

    def stream_window_events_url(self, *, port: int | None = None, include_credentials: bool = False) -> RtspUrl:
        """Build the RTSP URL of the event stream for the faulty front window topic.

        Open it with an RTSP client to receive the window events (declared as
        tns1:Device/tnsaxis:Window/Faulty).

        Builds the URL only; no request is made. Access: admin.
        """
        return self._device.rtsp_url_for(
            OPS.stream_window_events_url, {}, port=port, include_credentials=include_credentials
        )


class AsyncOpenCasingFaultyFrontWindowApi(AsyncApi):
    """Open Casing and Faulty Front Window (``open-casing-faulty-front-window``)."""

    INFO = INFO

    def stream_casing_events_url(self, *, port: int | None = None, include_credentials: bool = False) -> RtspUrl:
        """Build the RTSP URL of the event stream for the open casing topic.

        Open it with an RTSP client to receive the casing events (declared as
        tns1:Device/tnsaxis:Casing/Open).

        Builds the URL only; no request is made. Access: admin.
        """
        return self._device.rtsp_url_for(
            OPS.stream_casing_events_url, {}, port=port, include_credentials=include_credentials
        )

    def stream_window_events_url(self, *, port: int | None = None, include_credentials: bool = False) -> RtspUrl:
        """Build the RTSP URL of the event stream for the faulty front window topic.

        Open it with an RTSP client to receive the window events (declared as
        tns1:Device/tnsaxis:Window/Faulty).

        Builds the URL only; no request is made. Access: admin.
        """
        return self._device.rtsp_url_for(
            OPS.stream_window_events_url, {}, port=port, include_credentials=include_credentials
        )
