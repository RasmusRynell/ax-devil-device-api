"""Only None defaults a subscription list; the first header terminator wins in multipart parts."""

from __future__ import annotations

from typing import Any

import pytest

from ax_devil_device_api._runtime.ws_codecs import DataHubCodec, EventsCodec, datahub_setup, events_setup
from ax_devil_device_api._streams import MixedReplaceDecoder, Part


@pytest.mark.parametrize("bad", [{}, "", 0, False, b""])
def test_wrong_typed_falsy_subscriptions_raise(bad: Any) -> None:
    with pytest.raises(TypeError):
        datahub_setup({"subscriptions": bad})


@pytest.mark.parametrize("ok", [None, (), []])
def test_none_and_empty_sequences_mean_no_subscriptions(ok: Any) -> None:
    assert datahub_setup({"subscriptions": ok}) == []
    assert datahub_setup({}) == []


@pytest.mark.parametrize("bad", [{}, "", 0, False])
def test_wrong_typed_falsy_event_filters_raise(bad: Any) -> None:
    with pytest.raises(TypeError):
        events_setup({"event_filter_list": bad})


@pytest.mark.parametrize("codec", [EventsCodec(), DataHubCodec()])
@pytest.mark.parametrize("bad", ["", 0, False])
def test_wrong_typed_falsy_request_params_raise(codec: Any, bad: Any) -> None:
    with pytest.raises(TypeError):
        codec.encode_request("m", bad, "id")
    assert codec.encode_request("m", None, "id") is not None


# -- headers terminator: the earliest one ---------------------------------------------------------------------


def _parts(data: bytes, chunk: int | None) -> list[Part]:
    decoder = MixedReplaceDecoder("b")
    pieces = [data] if chunk is None else [data[i : i + chunk] for i in range(0, len(data), chunk)]
    out: list[Part] = []
    for piece in pieces:
        out += decoder.feed(piece)
    return out


@pytest.mark.parametrize("chunk", [None, 1, 2, 3, 5])
def test_lf_headers_with_crlfcrlf_in_the_body(chunk: int | None) -> None:
    data = b"--b\nContent-Type: text/plain\n\nfirst\r\n\r\nsecond\n--b\n\nnext\n--b--\n"
    parts = _parts(data, chunk)
    assert [p.body for p in parts] == [b"first\r\n\r\nsecond", b"next"]
    assert parts[0].headers.get("content-type") == "text/plain"


@pytest.mark.parametrize("chunk", [None, 1, 2, 3, 5])
def test_crlf_headers_with_lflf_in_the_body(chunk: int | None) -> None:
    data = b"--b\r\nContent-Type: text/plain\r\n\r\nfirst\n\nsecond\r\n--b--\r\n"
    parts = _parts(data, chunk)
    assert [p.body for p in parts] == [b"first\n\nsecond"]
    assert parts[0].headers.get("content-type") == "text/plain"
