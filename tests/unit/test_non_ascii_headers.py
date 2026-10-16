"""Non-ASCII outbound headers are refused locally (ConfigurationError, value not echoed), never a UnicodeEncodeError from the client."""

from __future__ import annotations

import io

import httpx
import pytest

from ax_devil_device_api._http.config import ConnectionConfig
from ax_devil_device_api._http.transport import AsyncTransport, SyncTransport
from ax_devil_device_api._http.types import FilePart, RawBody, Request
from ax_devil_device_api._http.upload import Upload
from ax_devil_device_api.errors import ConfigurationError


def _no_echo(error: Exception, *values: str) -> None:
    text = str(error) + repr(error) + str(error.args)
    assert not any(v in text for v in values), text


@pytest.mark.parametrize("name", ["X-Café", "Żółć"])
def test_a_non_ascii_header_name_is_refused(name: str) -> None:
    with pytest.raises(ConfigurationError, match="ASCII") as info:
        Request("GET", "/x", headers=((name, "v"),))
    _no_echo(info.value, name)


@pytest.mark.parametrize("value", ["café", "ünïcode", "日本語"])
def test_a_non_ascii_header_value_is_refused_without_echoing_it(value: str) -> None:
    with pytest.raises(ConfigurationError, match="ASCII") as info:
        Request("GET", "/x", headers=(("X-Note", value),))
    _no_echo(info.value, value)
    with pytest.raises(ConfigurationError, match="ASCII"):
        Request("GET", "/x", accept=value)


def test_a_non_ascii_content_type_is_refused() -> None:
    with pytest.raises(ConfigurationError, match="ASCII") as info:
        Upload(io.BytesIO(b""), 0, content_type="audio/café")
    _no_echo(info.value, "café")
    with pytest.raises(ConfigurationError, match="ASCII"):
        RawBody(b"x", "audio/café")
    with pytest.raises(ConfigurationError, match="ASCII"):
        FilePart("f", "n.bin", b"x", content_type="audio/café")


def test_non_ascii_file_names_still_work_in_multipart_bodies() -> None:
    assert FilePart("f", "café.bin", b"x").filename == "café.bin"  # carried in the UTF-8 body, not in an HTTP header


def _slipped_through(request: httpx.Request) -> httpx.Response:
    "é".encode("ascii")  # what httpx does with a header that got past validation
    return httpx.Response(200)


def test_sync_safety_net_maps_unicode_encode_errors() -> None:
    with SyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(_slipped_through)) as transport:
        with pytest.raises(ConfigurationError, match="cannot be encoded") as info:
            transport.send(Request("GET", "/x"))
    assert info.value.__cause__ is None and info.value.__context__ is None


def test_sync_stream_safety_net() -> None:
    with SyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(_slipped_through)) as transport:
        with pytest.raises(ConfigurationError, match="cannot be encoded"):
            with transport.open_stream(Request("GET", "/x", stream=True)):
                pass


@pytest.mark.anyio
async def test_async_and_async_stream_safety_net() -> None:
    async with AsyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(_slipped_through)) as transport:
        with pytest.raises(ConfigurationError, match="cannot be encoded"):
            await transport.send(Request("GET", "/x"))
        with pytest.raises(ConfigurationError, match="cannot be encoded"):
            async with transport.open_stream(Request("GET", "/x", stream=True)):
                pass
