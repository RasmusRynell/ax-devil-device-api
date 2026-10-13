"""Structural, fail-closed redaction of ``on_request`` records."""

from __future__ import annotations

import json
import random
import string
import time
from typing import Any
from urllib.parse import quote

import pytest

from ax_devil_device_api._http.debug import emit_request, redact_url, serialize
from ax_devil_device_api._http.types import FormBody, JsonBody, MultipartBody, Request
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


def test_xml_cdata_and_attributes() -> None:
    samples = [
        "<a:Password><![CDATA[SECRET]]></a:Password>",
        '<Login password="SECRET" user="u"/>',
        "<a:Token xmlns:a='x'>SECRET<b>SECRET</b></a:Token>",
        '<Cred><Password>SECRET</Password></Cred>',
        "<x><Password>SECRET",
    ]
    for sample in samples:
        assert "SECRET" not in json.dumps(serialize(sample)), sample
    assert "<Login" in serialize('<Login password="SECRET" user="u"/>') and 'user="u"' in serialize(
        '<Login password="SECRET" user="u"/>'
    )


def test_name_value_parameters_hide_the_value_of_secret_names() -> None:
    xml = [
        '<Parameters><Parameter Name="Password" Value="SECRET"/><Parameter Name="Host" Value="smtp.example"/></Parameters>',
        '<p name="smtpToken" value="SECRET"></p>',
        "<Parameter key='ftp_password'>SECRET</Parameter>",
        '<Parameter Name="password"><Value><![CDATA[SECRET]]></Value></Parameter>',
    ]
    for sample in xml:
        assert "SECRET" not in json.dumps(serialize(sample)), sample
    kept = serialize(xml[0])
    assert "smtp.example" in kept and 'Name="Password"' in kept
    for obj in ({"name": "Password", "value": "SECRET"}, {"Key": "api_key", "Value": "SECRET"}):
        assert "SECRET" not in json.dumps(serialize(obj)), obj
    assert serialize({"name": "Host", "value": "h"}) == {"name": "Host", "value": "h"}


def test_soap_action_body_is_never_exposed_by_the_hook() -> None:
    from ax_devil_device_api._http.types import RawBody

    body = RawBody(b'<Parameter Name="Password" Value="SECRET"/>', "application/soap+xml")
    assert "SECRET" not in _record(Request("POST", "/vapix/services", body=body))


def test_basic_prose_is_not_altered() -> None:
    for text in ("Basic functionality is supported", "Bearer of good news", "see https://example.com/@user for info"):
        assert serialize(text) == text


@pytest.mark.parametrize("size", [100_000, 1_000_000])
def test_large_ordinary_values_are_fast(size: int) -> None:
    value = "a" * size
    start = time.perf_counter()
    assert serialize(value) == value
    assert redact_url("https://g/?q=" + value).endswith(value)
    assert serialize({"k": ["x " * (size // 2)]})
    assert time.perf_counter() - start < 0.5


def test_large_json_string_and_separator_heavy_values_are_fast() -> None:
    start = time.perf_counter()
    big = json.dumps({"k": "a" * 1_000_000})
    assert serialize(big)
    for hostile in ("<a " * 300_000, "://" * 300_000, "a=" * 500_000, "%" * 1_000_000, "<![CDATA[" * 100_000):
        serialize(hostile)
        redact_url("https://g/?q=" + quote(hostile[:200_000]))
    assert time.perf_counter() - start < 5


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
    add("xml-element", Request("POST", "/x", body=JsonBody({"x": f"<a:Password>{tok}</a:Password>"})))
    add("xml-cdata", Request("POST", "/x", body=JsonBody({"x": f"<s><Token><![CDATA[{tok}]]></Token></s>"})))
    add("xml-attr", Request("POST", "/x", body=JsonBody({"x": f'<s Password="{tok}"/>'})))
    add("param-xml", Request("POST", "/x", body=JsonBody({"x": f'<P Name="smtp_password" Value="{tok}"/>'})))
    add("param-xml-text", Request("POST", "/x", body=JsonBody({"x": f"<P key='token'>{tok}</P>"})))
    add("param-json", Request("POST", "/x", body=JsonBody({"params": [{"Name": "password", "Value": tok}]})))
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
