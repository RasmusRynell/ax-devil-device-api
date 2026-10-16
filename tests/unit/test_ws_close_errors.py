"""A transport error while closing the WebSocket handshake response is mapped when closing is the primary operation and never
replaces the setup or body exception."""

from __future__ import annotations

import httpx
import pytest
from ws_fake import FakeWsCamera, events_handler

from ax_devil_device_api import AsyncDevice, Device, errors
from ax_devil_device_api._http.options import Heartbeat, RequestOptions
from ax_devil_device_api._runtime.ws import EVENTS
from ax_devil_device_api._runtime.ws_codecs import EventFilter

QUICK = Heartbeat(None)
FILTERS = [EventFilter(topic_filter="tns1:PTZController/tnsaxis:PTZReady")]
SECRET = "ws-close-secret-1"


@pytest.fixture
def bad_close(monkeypatch: pytest.MonkeyPatch) -> None:
    """Closing the handshake response fails. httpx closes a response once while building it (reading the empty body), so
    the failure is raised from the second close, the one the transport makes when the session ends."""
    original_close = httpx.Response.close
    original_aclose = httpx.Response.aclose

    def close(self: httpx.Response) -> None:
        original_close(self)
        if self.status_code == 101:
            self.extensions["closes"] = self.extensions.get("closes", 0) + 1
            if self.extensions["closes"] >= 2:
                raise httpx.ReadError(f"connection reset while closing {SECRET}")

    async def aclose(self: httpx.Response) -> None:
        await original_aclose(self)
        if self.status_code == 101:
            self.extensions["closes"] = self.extensions.get("closes", 0) + 1
            if self.extensions["closes"] >= 2:
                raise httpx.ReadError(f"connection reset while closing {SECRET}")

    monkeypatch.setattr(httpx.Response, "close", close)
    monkeypatch.setattr(httpx.Response, "aclose", aclose)


def device(camera: FakeWsCamera) -> Device:
    return Device("cam.test", credentials=("root", "pass"), transport=camera.transport())


def adevice(camera: FakeWsCamera) -> AsyncDevice:
    return AsyncDevice("cam.test", credentials=("root", "pass"), transport=camera.async_transport())


@pytest.mark.usefixtures("bad_close")
def test_sync_close_failure_is_mapped_when_closing_is_the_primary_operation() -> None:
    camera = FakeWsCamera(handler=events_handler)
    dev = device(camera)
    with pytest.raises(errors.ConnectionFailed) as info:
        with dev.connect_session(EVENTS, heartbeat=QUICK, event_filter_list=FILTERS):
            pass
    assert info.value.__cause__ is None and info.value.__context__ is None


@pytest.mark.usefixtures("bad_close")
def test_sync_close_failure_does_not_replace_a_body_exception() -> None:
    camera = FakeWsCamera(handler=events_handler)
    dev = device(camera)
    with pytest.raises(ValueError, match="body error"):
        with dev.connect_session(EVENTS, heartbeat=QUICK, event_filter_list=FILTERS):
            raise ValueError("body error")


@pytest.mark.usefixtures("bad_close")
def test_sync_close_failure_does_not_replace_a_setup_exception() -> None:
    camera = FakeWsCamera()  # never answers events:configure
    dev = device(camera)
    with pytest.raises(errors.ReadTimeout):
        with dev.connect_session(EVENTS, heartbeat=QUICK, event_filter_list=FILTERS, request_options=RequestOptions(timeout=0.2)):
            pass


@pytest.mark.anyio
@pytest.mark.usefixtures("bad_close")
async def test_async_close_failure_is_mapped_when_closing_is_the_primary_operation() -> None:
    camera = FakeWsCamera(handler=events_handler)
    dev = adevice(camera)
    with pytest.raises(errors.ConnectionFailed) as info:
        async with dev.connect_session(EVENTS, heartbeat=QUICK, event_filter_list=FILTERS):
            pass
    assert info.value.__cause__ is None and info.value.__context__ is None


@pytest.mark.anyio
@pytest.mark.usefixtures("bad_close")
async def test_async_close_failure_does_not_replace_a_body_exception() -> None:
    camera = FakeWsCamera(handler=events_handler)
    dev = adevice(camera)
    with pytest.raises(ValueError, match="body error"):
        async with dev.connect_session(EVENTS, heartbeat=QUICK, event_filter_list=FILTERS):
            raise ValueError("body error")


@pytest.mark.anyio
@pytest.mark.usefixtures("bad_close")
async def test_async_close_failure_does_not_replace_a_setup_exception() -> None:
    camera = FakeWsCamera()
    dev = adevice(camera)
    with pytest.raises(errors.ReadTimeout):
        async with dev.connect_session(EVENTS, heartbeat=QUICK, event_filter_list=FILTERS, request_options=RequestOptions(timeout=0.2)):
            pass


# --- closing the httpx client itself ---------------------------------------------------------------------------------------------


def test_sync_client_close_failure_is_mapped_or_suppressed(monkeypatch: pytest.MonkeyPatch) -> None:
    from ax_devil_device_api._http.config import ConnectionConfig
    from ax_devil_device_api._http.transport import SyncTransport

    def broken(self: httpx.Client) -> None:
        raise httpx.ReadError("reset while closing the client")

    monkeypatch.setattr(httpx.Client, "close", broken)
    transport = SyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(lambda r: httpx.Response(200)))
    with pytest.raises(errors.ConnectionFailed) as info:
        transport.close()
    assert info.value.__cause__ is None and info.value.__context__ is None
    with pytest.raises(ValueError, match="body error"):
        with SyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(lambda r: httpx.Response(200))):
            raise ValueError("body error")


@pytest.mark.anyio
async def test_async_client_close_failure_is_mapped_or_suppressed(monkeypatch: pytest.MonkeyPatch) -> None:
    from ax_devil_device_api._http.config import ConnectionConfig
    from ax_devil_device_api._http.transport import AsyncTransport

    async def broken(self: httpx.AsyncClient) -> None:
        raise httpx.ReadError("reset while closing the client")

    monkeypatch.setattr(httpx.AsyncClient, "aclose", broken)
    transport = AsyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(lambda r: httpx.Response(200)))
    with pytest.raises(errors.ConnectionFailed):
        await transport.aclose()
    with pytest.raises(ValueError, match="body error"):
        async with AsyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(lambda r: httpx.Response(200))):
            raise ValueError("body error")
