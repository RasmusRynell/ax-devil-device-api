"""A 101 Switching Protocols answer to an authenticated WebSocket upgrade verifies the credentials."""

from __future__ import annotations

import base64

import httpx
import pytest

from ax_devil_device_api._http.auth import AxisAuth
from ax_devil_device_api._http.config import Credentials

BASIC = 'Basic realm="AXIS"'
DIGEST = 'Digest realm="AXIS", nonce="abc123", qop="auth", algorithm=MD5'


class Device:
    """Challenges anonymous requests; answers 101 to a signed upgrade."""

    def __init__(self, challenge: str) -> None:
        self.challenge = challenge
        self.seen: list[str | None] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        auth = request.headers.get("authorization")
        self.seen.append(auth)
        if auth is None:
            return httpx.Response(401, headers={"WWW-Authenticate": self.challenge})
        if self.challenge.startswith("Basic"):
            expected = "Basic " + base64.b64encode(b"root:pw").decode()
            return httpx.Response(101 if auth == expected else 401, headers={"WWW-Authenticate": self.challenge})
        return httpx.Response(101)  # the Digest response is not re-verified here; the flow under test is the client's


def upgrade() -> httpx.Request:
    return httpx.Request("GET", "https://cam/ws", headers={"Connection": "Upgrade", "Upgrade": "websocket"})


@pytest.mark.parametrize("challenge", [BASIC, DIGEST], ids=["basic", "digest"])
def test_sync_101_verifies_and_a_reconnect_starts_signed(challenge: str) -> None:
    device = Device(challenge)
    auth = AxisAuth(Credentials("root", "pw"))
    with httpx.Client(transport=httpx.MockTransport(device)) as client:
        assert client.send(upgrade(), auth=auth.for_request("required", True)).status_code == 101
        assert auth.has_verified_state
        device.seen.clear()
        assert client.send(upgrade(), auth=auth.for_request("required", True)).status_code == 101
    assert len(device.seen) == 1 and device.seen[0] is not None  # no anonymous attempt, no extra 401 round trip


@pytest.mark.anyio
@pytest.mark.parametrize("challenge", [BASIC, DIGEST], ids=["basic", "digest"])
async def test_async_101_verifies_and_a_reconnect_starts_signed(challenge: str) -> None:
    device = Device(challenge)
    auth = AxisAuth(Credentials("root", "pw"))
    async with httpx.AsyncClient(transport=httpx.MockTransport(device)) as client:
        assert (await client.send(upgrade(), auth=auth.for_request("required", True))).status_code == 101
        assert auth.has_verified_state
        device.seen.clear()
        assert (await client.send(upgrade(), auth=auth.for_request("required", True))).status_code == 101
    assert len(device.seen) == 1 and device.seen[0] is not None


def test_a_rejected_upgrade_is_not_verified() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, headers={"WWW-Authenticate": BASIC})

    auth = AxisAuth(Credentials("root", "wrong"))
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(Exception, match="rejected"):
            client.send(upgrade(), auth=auth.for_request("required", True))
    assert not auth.has_verified_state
