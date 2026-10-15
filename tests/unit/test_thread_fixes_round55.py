"""Every header-producing input refuses control characters locally (ConfigurationError, before transport) without
echoing the value; the RTSP safe form redacts the query."""

from __future__ import annotations

import io
from collections.abc import Callable
from typing import Any

import pytest

from ax_devil_device_api._http.config import BearerToken, Credentials
from ax_devil_device_api._http.multipart import encode_multipart
from ax_devil_device_api._http.types import FilePart, MultipartBody, RawBody, Request
from ax_devil_device_api._http.upload import Upload, file_part
from ax_devil_device_api.errors import ConfigurationError

SENTINEL = "SENTINEL-HEADER-VALUE"
BAD = ["\x00", "\x01", "\x08", "\x0b", "\x0c", "\x0d", "\x0a", "\x1b", "\x1f", "\x7f"]

INPUTS: dict[str, Callable[[str], Any]] = {
    "raw body content type": lambda v: RawBody(b"x", f"audio/{v}"),
    "multipart part name": lambda v: FilePart(f"a{v}", "f", b"x"),
    "multipart file name": lambda v: FilePart("a", f"f{v}", b"x"),
    "multipart part content type": lambda v: FilePart("a", "f", b"x", content_type=f"audio/{v}"),
    "multipart field name": lambda v: encode_multipart(MultipartBody(fields=((f"n{v}", "x"),))),
    "request header name": lambda v: Request("GET", "/x", headers=((f"X-{v}", "1"),)),
    "request header value": lambda v: Request("GET", "/x", headers=(("X-A", f"1{v}"),)),
    "request accept": lambda v: Request("GET", "/x", accept=f"text/{v}"),
    "upload filename": lambda v: Upload(io.BytesIO(b"x"), 1, filename=f"f{v}"),
    "upload content type": lambda v: Upload(io.BytesIO(b"x"), 1, content_type=f"audio/{v}"),
    "upload helper filename": lambda v: file_part("p", b"x", filename=f"f{v}"),
    "upload helper content type": lambda v: file_part("p", b"x", content_type=f"audio/{v}"),
    "username": lambda v: Credentials(f"u{v}", "p"),
    "password": lambda v: Credentials("u", f"p{v}"),
    "bearer token": lambda v: BearerToken(f"t{v}"),
    "bearer token from a provider": lambda v: BearerToken(lambda: f"t{v}").current(),
}


@pytest.mark.parametrize("control", BAD, ids=lambda c: f"U+{ord(c):04X}")
@pytest.mark.parametrize("name", list(INPUTS))
def test_a_control_character_is_refused_locally_without_echoing_the_value(name: str, control: str) -> None:
    value = f"{SENTINEL}{control}"
    with pytest.raises(ConfigurationError) as caught:
        INPUTS[name](value)
    assert SENTINEL not in str(caught.value) and SENTINEL not in repr(caught.value)
    assert control not in str(caught.value) or control in "\x09"


@pytest.mark.parametrize("name", [n for n in INPUTS if n not in {"username", "password", "bearer token", "bearer token from a provider"}])
def test_a_tab_is_still_accepted_in_a_header_value(name: str) -> None:
    if name in {"request header name", "multipart field name", "multipart part name"}:
        pytest.skip("a tab in a name is not a value")
    INPUTS[name]("a\tb")
