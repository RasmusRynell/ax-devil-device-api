"""With several usable Digest challenges the strongest is answered (SHA-512-256 > SHA-256 > MD5, qop=auth over none)."""

from __future__ import annotations

import hashlib
import re

import httpx
import pytest

from ax_devil_device_api._http.config import ConnectionConfig, Credentials
from ax_devil_device_api._http.transport import SyncTransport
from ax_devil_device_api._http.types import Request

PASSWORD = "pw"


def challenge(realm: str, algorithm: str, *, qop: bool = True) -> str:
    qop_part = ', qop="auth"' if qop else ""
    return f'Digest realm="{realm}", nonce="nonce-{realm}", algorithm={algorithm}{qop_part}'


class Device:
    def __init__(self, *offers: str) -> None:
        self.offers = offers
        self.authorization: list[str] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        auth = request.headers.get("authorization")
        if auth is None:
            return httpx.Response(401, headers=[(b"www-authenticate", offer.encode()) for offer in self.offers])
        self.authorization.append(auth)
        return httpx.Response(200)


def answered(*offers: str) -> dict[str, str]:
    device = Device(*offers)
    with SyncTransport(ConnectionConfig("cam", credentials=Credentials("root", PASSWORD)), transport=httpx.MockTransport(device)) as t:
        assert t.send(Request("GET", "/x")).status == 200
    fields = {m[0]: m[1] or m[2] for m in re.findall(r'(\w+)=(?:"([^"]*)"|([^,\s]+))', device.authorization[-1])}
    return fields


def check_response(fields: dict[str, str], hash_name: str) -> None:
    def h(text: str) -> str:
        return hashlib.new(hash_name, text.encode()).hexdigest()

    ha1 = h(f"root:{fields['realm']}:{PASSWORD}")
    ha2 = h(f"GET:{fields['uri']}")
    if "qop" in fields:
        expected = h(f"{ha1}:{fields['nonce']}:{fields['nc']}:{fields['cnonce']}:auth:{ha2}")
    else:
        expected = h(f"{ha1}:{fields['nonce']}:{ha2}")
    assert fields["response"] == expected


def test_sha256_listed_after_md5_is_the_one_used() -> None:
    fields = answered(challenge("md5", "MD5"), challenge("sha256", "SHA-256"))
    assert fields["algorithm"] == "SHA-256" and fields["realm"] == "sha256"
    check_response(fields, "sha256")


def test_the_order_of_the_offers_does_not_matter() -> None:
    fields = answered(challenge("sha256", "SHA-256"), challenge("md5", "MD5"))
    assert fields["algorithm"] == "SHA-256"
    check_response(fields, "sha256")


def test_sha512_256_beats_sha256_and_md5() -> None:
    try:
        hashlib.new("sha512_256")
    except ValueError:
        pytest.skip("this OpenSSL has no SHA-512/256")
    fields = answered(challenge("md5", "MD5"), challenge("sha256", "SHA-256"), challenge("strong", "SHA-512-256"))
    assert fields["algorithm"] == "SHA-512-256" and fields["realm"] == "strong"
    check_response(fields, "sha512_256")


def test_a_sess_variant_ranks_just_below_its_base() -> None:
    assert answered(challenge("sess", "SHA-256-sess"), challenge("base", "SHA-256"))["realm"] == "base"
    assert answered(challenge("md5", "MD5"), challenge("sess", "SHA-256-sess"))["realm"] == "sess"  # still above MD5


def test_qop_auth_is_preferred_over_none_for_the_same_algorithm() -> None:
    assert answered(challenge("plain", "SHA-256", qop=False), challenge("qop", "SHA-256"))["realm"] == "qop"
    assert answered(challenge("qop", "SHA-256"), challenge("plain", "SHA-256", qop=False))["realm"] == "qop"


def test_a_tie_keeps_the_header_order() -> None:
    assert answered(challenge("first", "SHA-256"), challenge("second", "SHA-256"))["realm"] == "first"


def test_unsupported_offers_are_skipped_and_basic_is_still_never_chosen_over_digest() -> None:
    fields = answered(challenge("odd", "SHA3-999"), 'Basic realm="AXIS"', challenge("md5", "MD5"))
    assert fields["realm"] == "md5"
    with pytest.raises(Exception, match="unsupported Digest algorithm"):
        answered(challenge("odd", "SHA3-999"), 'Basic realm="AXIS"')
