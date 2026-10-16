"""D19 guard: a credential in a pair KEY is redacted in every serializer path; sensitive response headers are masked in repr."""

from __future__ import annotations

import json
from typing import Any

import pytest

from ax_devil_device_api._http.debug import emit_request, redact_request
from ax_devil_device_api._http.types import (
    FilePart,
    FormBody,
    Headers,
    JsonBody,
    MultipartBody,
    RawBody,
    Request,
    Response,
)

FORBIDDEN = ["hunter2", "u:p@"]
KEYS = ["password=hunter2", "rtsp://u:p@h/x"]


def _record(request: Request) -> str:
    events: list[dict[str, Any]] = []
    emit_request(events.append, request, "https://cam/x", 5.0, True)
    return json.dumps(events)


def _requests(key: str) -> dict[str, Request]:
    return {
        "query": Request("GET", "/x", query=((key, "v"), ("ok", "fine"))),
        "form": Request("POST", "/x", body=FormBody(((key, "v"), ("ok", "fine")))),
        "multipart field": Request("POST", "/x", body=MultipartBody(((key, "v"),), (FilePart("f", "n.bin", b"x"),))),
        "json": Request("POST", "/x", body=JsonBody({key: "v", "ok": "fine"})),
        "nested json": Request("POST", "/x", body=JsonBody({"a": [{key: "v"}]})),
        "raw": Request("POST", "/x", body=RawBody(b"x", "application/octet-stream")),
    }


@pytest.mark.parametrize("key", KEYS)
@pytest.mark.parametrize("path", sorted(_requests("k")))
def test_on_request_never_shows_a_credential_in_a_pair_key(path: str, key: str) -> None:
    shown = _record(_requests(key)[path])
    assert not any(bad in shown for bad in FORBIDDEN), shown


@pytest.mark.parametrize("key", KEYS)
@pytest.mark.parametrize("path", sorted(_requests("k")))
def test_the_public_request_copy_uses_the_same_key_redaction(path: str, key: str) -> None:
    assert not any(bad in repr(redact_request(_requests(key)[path])) for bad in FORBIDDEN)


def test_a_secret_key_redacts_the_value_and_ordinary_pairs_stay() -> None:
    shown = json.loads(_record(Request("GET", "/x", query=(("password=hunter2", "v"), ("ok", "fine")))))[0]["request"]["query"]
    assert ["ok", "fine"] in shown and ["password=<redacted>", "<redacted>"] in shown


def test_header_names_are_redacted_too() -> None:
    shown = _record(Request("GET", "/x", headers=(("X-Note-password=hunter2", "v"),)))
    assert "hunter2" not in shown


# --- Headers repr ---------------------------------------------------------------------------------------------------------------


def _headers() -> Headers:
    return Headers(
        [
            ("Content-Type", "text/plain"),
            ("Set-Cookie", "sid=SECRET-SESSION; HttpOnly"),
            ("Cookie", "sid=SECRET-SESSION"),
            ("Authorization", "Bearer SECRET-TOKEN"),
            ("Proxy-Authorization", "Basic SECRET-BASIC"),
            ("WWW-Authenticate", 'Digest realm="AXIS", nonce="SECRET-NONCE", opaque="SECRET-OPAQUE", qop="auth"'),
            ("X-Api-Token", "SECRET-API"),
            ("X-Request-Id", "visible-1"),
        ]
    )


def test_headers_repr_masks_sensitive_values() -> None:
    for shown in (repr(_headers()), str(_headers()), repr(Response(200, _headers(), b"", Request("GET", "/x")))):
        assert "SECRET" not in shown, shown
        assert "text/plain" in shown and "visible-1" in shown and "Digest" in shown


def test_lookup_and_raw_access_are_unchanged() -> None:
    headers = _headers()
    assert headers["set-cookie"] == "sid=SECRET-SESSION; HttpOnly"
    assert headers.get_all("www-authenticate")[0].startswith("Digest realm=")
    assert ("Authorization", "Bearer SECRET-TOKEN") in headers.items_raw
