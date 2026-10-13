"""Structural, fail-closed redaction of ``on_request`` records."""

from __future__ import annotations

import json
import random
import string
import time
from collections.abc import Callable
from typing import Any
from urllib.parse import quote

import httpx
import pytest

from ax_devil_device_api._http.config import ConnectionConfig
from ax_devil_device_api._http.debug import emit_request, redact_url, serialize
from ax_devil_device_api._http.transport import AsyncTransport, SyncTransport
from ax_devil_device_api._http.types import FormBody, JsonBody, MultipartBody, RawBody, Request
from ax_devil_device_api.apis.remote_object_storage import S3Destination
from ax_devil_device_api.testing import MockCamera

DESTINATIONS = "/config/rest/remote-object-storage/v1/destinations"


def _record(request: Request, url: str = "https://cam/x") -> str:
    events: list[dict[str, Any]] = []
    emit_request(events.append, request, url, 5.0, True)
    return json.dumps(events)


def _hook_text(**kwargs: Any) -> str:
    camera = MockCamera()
    camera.rest("POST", DESTINATIONS, status=201)
    events: list[dict[str, Any]] = []
    s3 = S3Destination(access_key_id="AKIA", secret_access_key="x", session_token="y")
    with camera.device(on_request=events.append) as dev:
        dev.apis.remote_object_storage.add_destination(id="d1", s3=s3, **kwargs)
    return json.dumps(events)


def test_query_value_with_key_and_encoded_url_through_the_hook() -> None:
    text = _hook_text(description="password=abc rtsp%3A%2F%2Froot%3ASECRET%40camera")
    assert "SECRET" not in text and "abc" not in text


def test_url_credential_encoded_five_layers_deep_fails_closed() -> None:
    value = "rtsp://root:SECRET@camera"
    for _ in range(5):
        value = quote(value, safe="")
    assert "SECRET" not in _hook_text(description=value)
    assert redact_url(f"https://g/?t={quote(value, safe='')}").count("SECRET") == 0
    assert serialize(value) == "<redacted>"


def test_credentials_in_encoded_fragment() -> None:
    inner = quote("rtsp://root:SECRET@camera", safe="")
    for url in (f"https://g/p#{inner}", f"https://g/p#{quote(inner, safe='')}", "https://g/p#a=1&password=SECRET"):
        assert "SECRET" not in redact_url(url), url


def test_credentials_are_redacted_at_every_layer_not_just_the_first() -> None:
    text = "rtsp://a:FIRST@h/?u=" + quote("rtsp://b:SECOND@h", safe="")
    out = serialize(text)
    assert "FIRST" not in out and "SECOND" not in out


@pytest.mark.parametrize("name", ["Cookie", "cookie", "Set-Cookie", "Authorization", "PROXY-AUTHORIZATION", "X-Api-Key"])
def test_sensitive_headers_are_dropped_wholesale(name: str) -> None:
    for value in ("sid=SECRET; other=SECONDSECRET", "Basic YTpi", "Bearer SECRET", "Digest username=SECRET"):
        text = _record(Request("GET", "/x", headers=((name, value),)))
        assert "SECRET" not in text and "YTpi" not in text, (name, value)
        assert "<redacted>" in text


def test_non_sensitive_headers_are_kept() -> None:
    text = _record(Request("GET", "/x", headers=(("X-Trace", "abc"),)))
    assert "abc" in text


def test_name_value_parameters_hide_the_value_of_secret_names() -> None:
    structured = [
        {"name": "Password", "value": "SECRET"},
        {"Key": "api_key", "Value": "SECRET"},
        {"@Name": "smtp_password", "@Value": "SECRET"},
        {"tt:Name": "Token", "tt:Value": "SECRET"},
        {"Parameters": {"Parameter": [{"@Name": "Host", "@Value": "h"}, {"@NAME": "ftpPassword", "@VALUE": "SECRET"}]}},
    ]
    for obj in structured:
        assert "SECRET" not in json.dumps(serialize(obj)), obj
    assert serialize({"@Name": "Host", "@Value": "h"}) == {"@Name": "Host", "@Value": "h"}
    assert serialize({"name": "Password", "value": "SECRET"})["name"] == "Password"


def test_overlapping_and_odd_userinfo_is_redacted_through_the_hook() -> None:
    for desc in (
        "rtsp://a:FIRST@h,rtsp://b:SECOND@h",
        "rtsp://u:ABC'SECRET@camera",
        'x rtsp://u:a,b"SECRET@camera/p',
        "rtsp://u@v:SECRET@camera",
    ):
        text = _hook_text(description=desc)
        assert not any(w in text for w in ("FIRST", "SECOND", "SECRET")), desc


def test_userinfo_is_redacted_before_keyed_pairs() -> None:
    enc = quote("rtsp://root:ABC=DEF@camera", safe="")
    for desc in (
        "password=x rtsp://root:ABC=DEF@camera",
        "a=1&password=x&u=rtsp://root:ABC=DEF@camera",
        "rtsp://a:AAA=BBB&CCC@h password=x rtsp://b:DDD=EEE@h token=y rtsp://c:FFF@h",
        f"password=x {enc}",
        f"a=1&token=x&u={enc}",
    ):
        text = _hook_text(description=desc)
        assert not any(w in text for w in ("ABC", "DEF", "AAA", "BBB", "CCC", "DDD", "EEE", "FFF")), desc


def test_markup_does_not_split_an_assignment_from_its_value() -> None:
    for desc in ("password=<ABC123>", "password=ABC<foo>123", "x=1&token=<a href='SECRET'>"):
        text = _hook_text(description=desc)
        assert "ABC" not in text and "SECRET" not in text, desc


def test_markup_comment_cannot_hide_a_value() -> None:
    for desc in ("password=<!--x>SECRET-->", "password='<!-- > --> SECRET'"):
        assert "SECRET" not in _hook_text(description=desc), desc


def _raw_bodies() -> list[RawBody]:
    def chunks() -> Any:
        yield b"<Password>SECRET</Password>"

    return [
        RawBody(b"<Password>SECRET</Password>", "text/xml"),
        RawBody(b"SECRET", "application/octet-stream"),
        RawBody(b"password=SECRET", "text/plain"),
        RawBody(b'<P Name="Password" Value="SECRET"/>', "application/soap+xml"),
        RawBody(b'{"password": "SECRET"}', "application/json"),
        RawBody(chunks(), "text/xml"),
    ]


def test_raw_bodies_are_never_logged() -> None:
    for body in _raw_bodies():
        text = _record(Request("POST", "/x", body=body))
        assert "SECRET" not in text
        assert body.content_type in text


def test_raw_bodies_are_never_logged_by_the_sync_transport() -> None:
    events: list[dict[str, Any]] = []
    cfg = ConnectionConfig("cam", on_request=events.append)
    with SyncTransport(cfg, transport=httpx.MockTransport(lambda r: httpx.Response(200))) as t:
        for body in _raw_bodies():
            t.send(Request("POST", "/x", body=body))
    assert len(events) == 6 and "SECRET" not in json.dumps(events)


@pytest.mark.anyio
async def test_raw_bodies_are_never_logged_by_the_async_transport() -> None:
    events: list[dict[str, Any]] = []
    cfg = ConnectionConfig("cam", on_request=events.append)
    async with AsyncTransport(cfg, transport=httpx.MockTransport(lambda r: httpx.Response(200))) as t:
        for body in _raw_bodies()[:5]:
            await t.send(Request("POST", "/x", body=body))
    assert len(events) == 5 and "SECRET" not in json.dumps(events)


def test_basic_prose_is_not_altered() -> None:
    for text in ("Basic functionality is supported", "Bearer of good news", "see https://example.com/@user for info"):
        assert serialize(text) == text


def _best(fn: Callable[[], Any], runs: int = 3) -> float:
    best = float("inf")
    for _ in range(runs):
        start = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - start)
    return best


def assert_scales_linearly(work: Callable[[int], Any], n: int, label: str) -> None:
    """``work(n)`` must scale about linearly: best-of-3 time at 4n over time at n stays below 8
    (linear code gives about 4, quadratic about 16). Wall-clock noise on a shared runner cannot trip this
    the way an absolute bound can; a generous ceiling at 4n still catches catastrophic slowness."""
    small = _best(lambda: work(n))
    large = _best(lambda: work(4 * n))
    assert large < 5, f"{label}: {large:.2f} s at {4 * n}"
    assert large / max(small, 1e-4) < 8, f"{label}: {small:.4f} s at {n} but {large:.4f} s at {4 * n}"


def _ordinary(n: int) -> None:
    value = "a" * n
    assert serialize(value) == value
    assert redact_url("https://g/?q=" + value).endswith(value)
    assert serialize({"k": ["x " * (n // 2)]})


def test_large_ordinary_values_scale_linearly() -> None:
    assert_scales_linearly(_ordinary, 250_000, "ordinary")


def _described(text: str) -> None:
    serialize(text)
    redact_url("https://g/?q=" + quote(text[: len(text) * 3 // 10]))


HOSTILE = {
    "json string": lambda n: json.dumps({"k": "a" * n}),
    "open tag": lambda n: "<x " + "a" * n + ">",
    "attributes": lambda n: '<x a="b" ' * (n // 10) + ">",
    "quoted words": lambda n: "<x " + "'a' " * (n // 4) + ">",
    "userinfo list": lambda n: "rtsp://a:b@h," * (n // 14),
    "at signs": lambda n: "@" * n,
    "schemes": lambda n: "://" * (n // 3),
    "scheme and at signs": lambda n: "://" + "@" * n,
    "quotes after key": lambda n: "password=" + "'" * n,
    "words after key": lambda n: "password=" + "a b " * (n // 4),
    "open markup": lambda n: "<a " * (n // 3),
    "equals": lambda n: "a=" * (n // 2),
    "percent": lambda n: "%" * n,
    "cdata": lambda n: "<![CDATA[" * (n // 9),
}


@pytest.mark.parametrize("name", sorted(HOSTILE))
def test_hostile_values_scale_linearly(name: str) -> None:
    build = HOSTILE[name]
    assert_scales_linearly(lambda n: _described(build(n)), 250_000, name)


def test_scale_check_detects_quadratic_work() -> None:
    def quadratic(n: int) -> int:
        total = 0
        for i in range(n // 100):
            total += sum(1 for _ in range(n // 100))
        return total

    with pytest.raises(AssertionError):
        assert_scales_linearly(quadratic, 20_000, "quadratic")
    assert_scales_linearly(lambda n: sum(1 for _ in range(n)), 200_000, "linear")


# --- property-style: a known secret never survives any supported carrier -------------------------------------------

_TOKENS = ["x", "Zq", "SECRET", "p4ss", "AbC123xyz", "Tok_en-9"]
_RNG = random.Random(1234)
_TOKENS += ["".join(_RNG.choices(string.ascii_letters + string.digits, k=_RNG.randint(1, 24))) for _ in range(20)]


def _enc(value: str, layers: int) -> str:
    for _ in range(layers):
        value = quote(value, safe="")
    return value


def _carriers(tok: str) -> list[tuple[str, Request, str]]:
    url = f"rtsp://root:{tok}@camera/stream"
    out: list[tuple[str, Request, str]] = []

    def add(label: str, request: Request, u: str = "https://cam/x") -> None:
        out.append((label, request, u))

    add("header-auth", Request("GET", "/x", headers=(("Authorization", tok),)))
    add("header-cookie", Request("GET", "/x", headers=(("cookie", f"a=1; sid={tok}"),)))
    add("query-key", Request("GET", "/x", query=(("password", tok),)))
    add("form-key", Request("POST", "/x", body=FormBody((("api_key", tok),))))
    add("json-depth", Request("POST", "/x", body=JsonBody({"a": [{"b": {"clientSecret": tok}}]})))
    add("json-string", Request("POST", "/x", body=JsonBody({"a": json.dumps({"password": tok})})))
    add("multipart", Request("POST", "/x", body=MultipartBody(fields=(("token", tok),))))
    add("param-soap", Request("POST", "/x", body=JsonBody({"Parameter": [{"@Name": "smtp_password", "@Value": tok}]})))
    add("param-prefixed", Request("POST", "/x", body=JsonBody({"tt:Name": "Token", "tt:Value": tok})))
    add("param-json", Request("POST", "/x", body=JsonBody({"params": [{"Name": "password", "Value": tok}]})))
    add("userinfo-overlap", Request("POST", "/x", body=JsonBody({"d": f"rtsp://a:{tok}@h,rtsp://b:{tok}@h"})))
    add("userinfo-eq", Request("POST", "/x", body=JsonBody({"d": f"password=x rtsp://root:A={tok}&B@camera"})))
    add("userinfo-eq-enc", Request("GET", "/x", query=(("d", _enc(f"a=1&token=x&u=rtsp://r:A={tok}@h", 1)),)))
    add("userinfo-quote", Request("POST", "/x", body=JsonBody({"d": f"rtsp://u:a'{tok}@h"})))
    add("kv-markup", Request("POST", "/x", body=JsonBody({"d": f"password=<{tok}>x<y>{tok}"})))
    add("userinfo-text", Request("POST", "/x", body=JsonBody({"d": f"see {url} now"})))
    add("userinfo-form", Request("POST", "/x", body=FormBody((("d", url),))))
    add("userinfo-query", Request("GET", "/x", query=(("u", url),)))
    add("userinfo-url-query", Request("GET", "/x"), f"https://cam/x?u={quote(url, safe='')}")
    add("userinfo-fragment", Request("GET", "/x"), f"https://cam/x#{url}")
    add("kv-in-query", Request("GET", "/x", query=(("d", f"a=1&password={tok}"),)))
    for layers in (1, 2, 3):
        add(f"enc{layers}-query", Request("GET", "/x", query=(("u", _enc(url, layers)),)))
        add(f"enc{layers}-url", Request("GET", "/x"), f"https://cam/x?u={_enc(url, layers)}")
        add(f"enc{layers}-fragment", Request("GET", "/x"), f"https://cam/x#{_enc(url, layers)}")
        add(f"enc{layers}-json", Request("POST", "/x", body=JsonBody({"d": _enc(url, layers)})))
        add(f"enc{layers}-kv", Request("GET", "/x", query=(("d", _enc(f"x=1&token={tok}", layers)),)))
    return out


@pytest.mark.parametrize("tok", _TOKENS)
def test_known_secret_never_appears_in_any_carrier(tok: str) -> None:
    for label, request, url in _carriers(tok):
        text = _record(request, url)
        assert f"{tok}@" not in text and f":{tok}" not in text, label
        if len(tok) >= 4:
            assert tok not in text, label


@pytest.mark.parametrize("length", [1, 2, 3, 8])
def test_output_is_independent_of_the_secret_value(length: int) -> None:
    """Short tokens collide with ordinary text, so compare two different secrets of equal length instead."""
    first = "Q" * length
    second = "7" * length
    for (label, req_a, url_a), (_, req_b, url_b) in zip(_carriers(first), _carriers(second), strict=True):
        assert _record(req_a, url_a) == _record(req_b, url_b), label
