"""on_request, on_response and the DEBUG log show a request path the same way (one redactor, the request's masked names)."""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlsplit

import httpx
import pytest

from ax_devil_device_api._http.config import ConnectionConfig
from ax_devil_device_api._http.debug import redact_path
from ax_devil_device_api._http.transport import AsyncTransport, SyncTransport
from ax_devil_device_api._http.types import Request
from ax_devil_device_api._runtime.driver import Call, run_async, run_sync

PATH = "/api/serialno=SECRET123/items/password=hunter2/rtsp%3A%2F%2Fu%3Ap%40h/ok"
MASKED = frozenset({"serialno"})
FORBIDDEN = ["SECRET123", "hunter2", "u:p@", "u%3Ap%40h"]


def _flow() -> Any:
    response = yield Request("GET", PATH, masked=MASKED)
    return response.status


def _ok(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200)


def _config(requests: list[dict[str, Any]], responses: list[dict[str, Any]]) -> ConnectionConfig:
    return ConnectionConfig("cam", on_request=requests.append, on_response=responses.append)


def _assert_parity(requests: list[dict[str, Any]], responses: list[dict[str, Any]], caplog: pytest.LogCaptureFixture) -> None:
    assert len(requests) == len(responses) == 1
    shown_in_request = urlsplit(requests[0]["request"]["url"]).path
    assert responses[0]["path"] == shown_in_request
    debug_line = next(r.getMessage() for r in caplog.records if "->" in r.getMessage())
    assert shown_in_request in debug_line
    everything = repr((requests, responses)) + debug_line
    assert not any(bad in everything for bad in FORBIDDEN)
    assert shown_in_request.startswith("/api/")  # the redactor works on the text; the rest of the path is its call


def test_sync_records_and_debug_log_agree(caplog: pytest.LogCaptureFixture) -> None:
    requests: list[dict[str, Any]] = []
    responses: list[dict[str, Any]] = []
    caplog.set_level(logging.DEBUG, logger="ax_devil_device_api")
    with SyncTransport(_config(requests, responses), transport=httpx.MockTransport(_ok)) as transport:
        assert run_sync(transport, _flow(), Call(label=("a", "b"), on_response=responses.append)) == 200
    _assert_parity(requests, responses, caplog)


@pytest.mark.anyio
async def test_async_records_and_debug_log_agree(caplog: pytest.LogCaptureFixture) -> None:
    requests: list[dict[str, Any]] = []
    responses: list[dict[str, Any]] = []
    caplog.set_level(logging.DEBUG, logger="ax_devil_device_api")
    async with AsyncTransport(_config(requests, responses), transport=httpx.MockTransport(_ok)) as transport:
        assert await run_async(transport, _flow(), Call(label=("a", "b"), on_response=responses.append)) == 200
    _assert_parity(requests, responses, caplog)


def test_the_masked_list_is_per_request() -> None:
    assert "SECRET123" not in redact_path(PATH, MASKED)
    assert "serialno=SECRET123" in redact_path("/api/serialno=SECRET123/x")  # not masked on a request that does not mask it


def test_a_path_starting_with_two_slashes_is_not_taken_for_a_host() -> None:
    assert redact_path("//a/b") == "//a/b"
