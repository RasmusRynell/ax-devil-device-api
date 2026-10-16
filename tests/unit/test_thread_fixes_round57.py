"""The handshake response carries a redacted copy of its request; a '#' in a request path is refused."""

from __future__ import annotations

from typing import Any

import pytest
from ws_fake import FakeWsCamera

from ax_devil_device_api import AsyncDevice, Device
from ax_devil_device_api._http.config import ConnectionConfig
from ax_devil_device_api._http.options import Heartbeat
from ax_devil_device_api._http.types import Request
from ax_devil_device_api._runtime.ws import EVENTS, SessionSpec
from ax_devil_device_api.errors import ConfigurationError
from ax_devil_device_api.rtsp import build_rtsp_url

QUICK = Heartbeat(None)


def _assert_redacted(camera: FakeWsCamera, response: Any) -> None:
    token = camera.token
    request = response.request
    assert token not in repr(response) and token not in repr(request)
    assert token not in repr(request.query) and all(token not in str(value) for _, value in request.query)
    assert any(key == "wssession" for key, _ in request.query), "the parameter is still there, redacted"
    assert camera.ws_requests[0].url.params["wssession"] == token, "the real request carried the token"


def test_sync_the_handshake_response_carries_a_redacted_request() -> None:
    camera = FakeWsCamera()
    with Device("cam.test", credentials=("root", "pass"), transport=camera.transport()) as dev:
        with dev.connect_session(EVENTS, heartbeat=QUICK, use_token=True) as session:
            _assert_redacted(camera, session.response)
            assert session.response.status == 101


@pytest.mark.anyio
async def test_async_the_handshake_response_carries_a_redacted_request() -> None:
    camera = FakeWsCamera()
    async with AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport()) as dev:
        async with dev.connect_session(EVENTS, heartbeat=QUICK, use_token=True) as session:
            _assert_redacted(camera, session.response)


# -- '#' in a path ------------------------------------------------------------------------------------------------------


def test_a_fragment_delimiter_in_a_request_path_is_refused_without_echoing_it() -> None:
    with pytest.raises(ConfigurationError) as caught:
        Request("GET", "/vapix/ws#SENTINEL-ALT")
    assert "SENTINEL" not in str(caught.value)


def test_an_encoded_hash_is_allowed() -> None:
    assert Request("GET", "/vapix/a%23b").path == "/vapix/a%23b"
    build_rtsp_url("cam", path="/a%23b")  # accepted (the RTSP path is quoted as given)
    assert SessionSpec("api", "/vapix/a%23b").path == "/vapix/a%23b"


@pytest.mark.parametrize(
    "build",
    [
        lambda: Request("GET", "/x#alt"),
        lambda: Request("GET", "/#"),
        lambda: SessionSpec("api", "/vapix/ws#alt"),
        lambda: SessionSpec("api", "/vapix/ws", token_path="/axis-cgi/wssession.cgi#alt"),
        lambda: build_rtsp_url("cam", path="/axis-media/media.amp#alt"),
        lambda: ConnectionConfig("cam", base_path="/vapix#alt"),
    ],
    ids=["request", "request bare hash", "session path", "session token path", "rtsp path", "base path"],
)
def test_every_path_entry_point_refuses_a_fragment_delimiter(build: Any) -> None:
    with pytest.raises(ConfigurationError) as caught:
        build()
    assert "alt" not in str(caught.value)


def test_a_path_parameter_with_a_hash_is_encoded_not_sent_as_a_fragment() -> None:
    spec = SessionSpec("api", "/vapix/{name}/ws").bind({"name": "a#b"})
    assert spec.path == "/vapix/a%23b/ws"
