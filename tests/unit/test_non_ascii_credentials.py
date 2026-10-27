"""Non-ASCII user names and tokens are refused when built; non-ASCII passwords work (UTF-8) for Digest and Basic."""

from __future__ import annotations

import base64
import hashlib
import io
import json
import re

import httpx
import pytest

from ax_devil_device_api import cli
from ax_devil_device_api._http.auth import AxisAuth
from ax_devil_device_api._http.config import BearerToken, ConnectionConfig, Credentials
from ax_devil_device_api._http.transport import AsyncTransport, SyncTransport
from ax_devil_device_api._http.types import Request
from ax_devil_device_api.errors import ConfigurationError

PASSWORD = "pässwörd✓"
DIGEST = 'Digest realm="AXIS", nonce="abc123", qop="auth", algorithm=MD5'
BASIC = 'Basic realm="AXIS"'


@pytest.mark.parametrize("username", ["josé", "ユーザー", "rooté", "é"])
def test_a_non_ascii_username_is_refused_without_echoing_it(username: str) -> None:
    with pytest.raises(ConfigurationError, match="ASCII") as info:
        Credentials(username, "pw")
    assert username not in str(info.value) and username not in repr(info.value) and "jos" not in str(info.value)


def test_a_non_ascii_bearer_token_is_refused() -> None:
    with pytest.raises(ConfigurationError, match="ASCII"):
        BearerToken("tökén")
    with pytest.raises(ConfigurationError, match="ASCII"):
        BearerToken(lambda: "tökén").current()


def test_ascii_usernames_and_non_ascii_passwords_are_accepted() -> None:
    assert Credentials("root", PASSWORD).password == PASSWORD


class Device:
    """Challenges, then checks nothing: it returns 200 to any signed request and remembers the Authorization header."""

    def __init__(self, challenge: str) -> None:
        self.challenge = challenge
        self.authorization: list[str] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        auth = request.headers.get("authorization")
        if auth is None:
            return httpx.Response(401, headers=[(b"www-authenticate", self.challenge.encode("utf-8"))])
        self.authorization.append(auth)
        return httpx.Response(200, text="ok")


def _check_digest(header: str) -> None:
    fields = dict(re.findall(r'(\w+)=(?:"([^"]*)"|([^,\s]+))', header) and [(m[0], m[1] or m[2]) for m in re.findall(r'(\w+)=(?:"([^"]*)"|([^,\s]+))', header)])

    def h(text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    ha1 = h(f"root:AXIS:{PASSWORD}")
    ha2 = h(f"GET:{fields['uri']}")
    assert fields["response"] == h(f"{ha1}:{fields['nonce']}:{fields['nc']}:{fields['cnonce']}:auth:{ha2}")


def test_sync_digest_hashes_a_non_ascii_password_as_utf8() -> None:
    device = Device(DIGEST)
    with SyncTransport(ConnectionConfig("cam", credentials=Credentials("root", PASSWORD)), transport=httpx.MockTransport(device)) as t:
        assert t.send(Request("GET", "/x")).status == 200
    _check_digest(device.authorization[-1])


def test_sync_basic_encodes_a_non_ascii_password_as_utf8() -> None:
    device = Device(BASIC)
    with SyncTransport(ConnectionConfig("cam", credentials=Credentials("root", PASSWORD)), transport=httpx.MockTransport(device)) as t:
        assert t.send(Request("GET", "/x")).status == 200
    assert base64.b64decode(device.authorization[-1].split()[1]).decode("utf-8") == f"root:{PASSWORD}"


@pytest.mark.anyio
@pytest.mark.parametrize("challenge", [DIGEST, BASIC], ids=["digest", "basic"])
async def test_async_non_ascii_password_works(challenge: str) -> None:
    device = Device(challenge)
    async with AsyncTransport(ConnectionConfig("cam", credentials=Credentials("root", PASSWORD)), transport=httpx.MockTransport(device)) as t:
        assert (await t.send(Request("GET", "/x"))).status == 200
    assert device.authorization


def test_a_non_ascii_challenge_parameter_is_a_configuration_error_not_a_unicode_error() -> None:
    device = Device('Digest realm="réalm", nonce="abc123", qop="auth", algorithm=MD5')
    with SyncTransport(ConnectionConfig("cam", credentials=Credentials("root", "pw")), transport=httpx.MockTransport(device)) as t:
        with pytest.raises(ConfigurationError, match="Authorization header") as info:
            t.send(Request("GET", "/x"))
    assert "réalm" not in str(info.value)


def test_the_safety_net_in_the_auth_flow_itself() -> None:
    device = Device('Digest realm="réalm", nonce="n", qop="auth", algorithm=MD5')
    auth = AxisAuth(Credentials("root", "pw"))
    with httpx.Client(transport=httpx.MockTransport(device)) as client:
        with pytest.raises(ConfigurationError):
            client.send(httpx.Request("GET", "https://cam/x"), auth=auth.for_request("required", True))


def test_the_cli_refuses_a_non_ascii_user_without_echoing_it() -> None:
    out, err = io.StringIO(), io.StringIO()
    code = cli.main(["--host", "cam", "--user", "josé", "--password", "pw", "call", "mqtt_client", "get_client_status"], out=out, err=err)
    assert code != 0 and "josé" not in out.getvalue() + err.getvalue()
    assert "ASCII" in json.loads(err.getvalue().splitlines()[-1])["error"]["message"]
