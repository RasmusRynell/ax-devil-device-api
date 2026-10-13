"""Streamed (non-replayable) bodies verify the credentials with a preflight GET first."""

from __future__ import annotations

import hashlib
import re

import httpx
import pytest

from ax_devil_device_api._http.config import ConnectionConfig, Credentials
from ax_devil_device_api._http.transport import PREFLIGHT_PATH, AsyncTransport, SyncTransport
from ax_devil_device_api._http.types import RawBody, Request
from ax_devil_device_api.errors import AuthError

CHALLENGE = 'Digest realm="AXIS", nonce="n1", qop="auth", algorithm=MD5'


class Camera:
    """Digest device; ``preflight_status`` overrides the answer to an authenticated preflight."""

    def __init__(self, password: str = "pw", preflight_status: int | None = None) -> None:
        self.password = password
        self.preflight_status = preflight_status
        self.seen: list[tuple[str, str, bool, bytes]] = []  # method, path, authorized, body
        self.stale = False  # the next authorized request is answered 401 once (expired nonce)

    def _valid(self, request: httpx.Request, auth: str) -> bool:
        f = {m[0]: m[1] or m[2] for m in re.findall(r'(\w+)=(?:"([^"]*)"|([^,\s]+))', auth)}
        h = lambda s: hashlib.md5(s.encode()).hexdigest()  # noqa: E731
        ha1 = h(f"root:AXIS:{self.password}")
        ha2 = h(f"{request.method}:{request.url.raw_path.decode()}")
        return f.get("response") == h(f"{ha1}:{f['nonce']}:{f['nc']}:{f['cnonce']}:auth:{ha2}")

    def __call__(self, request: httpx.Request) -> httpx.Response:
        auth = request.headers.get("authorization")
        ok = auth is not None and self._valid(request, auth)
        if ok and self.stale and request.url.path == PREFLIGHT_PATH:
            self.stale = False
            ok = False
        self.seen.append((request.method, request.url.path, auth is not None, request.content))
        if not ok:
            return httpx.Response(401, headers={"WWW-Authenticate": CHALLENGE})
        if request.url.path == PREFLIGHT_PATH and self.preflight_status is not None:
            return httpx.Response(self.preflight_status)
        return httpx.Response(200)

    @property
    def paths(self) -> list[tuple[str, str]]:
        return [(m, p) for m, p, _, _ in self.seen]


def upload(chunks: list[bytes] | None = None) -> Request:
    chunks = chunks or [b"ab", b"cd"]
    return Request("POST", "/up", body=RawBody(iter(chunks), "application/octet-stream", size=sum(map(len, chunks))))


def cfg(password: str = "pw") -> ConnectionConfig:
    return ConnectionConfig("cam", credentials=Credentials("root", password))


def test_streamed_upload_verifies_first_then_streams_once() -> None:
    cam = Camera()
    with SyncTransport(cfg(), transport=httpx.MockTransport(cam)) as t:
        assert t.send(upload()).status == 200
    assert cam.paths == [("GET", PREFLIGHT_PATH), ("GET", PREFLIGHT_PATH), ("POST", "/up")]
    post = cam.seen[-1]
    assert post[2] and post[3] == b"abcd"  # sent once, signed, with the whole body


def test_verified_credentials_are_reverified_before_every_one_shot_body() -> None:
    cam = Camera()
    with SyncTransport(cfg(), transport=httpx.MockTransport(cam)) as t:
        t.send(Request("GET", "/other"))
        cam.seen.clear()
        t.send(upload())
        t.send(upload([b"x"]))
    assert cam.paths == [("GET", PREFLIGHT_PATH), ("POST", "/up")] * 2


def test_stale_nonce_is_renewed_by_the_preflight_not_the_body() -> None:
    cam = Camera()
    with SyncTransport(cfg(), transport=httpx.MockTransport(cam)) as t:
        t.send(Request("GET", "/other"))
        cam.password = "pw"
        cam.stale = True
        cam.seen.clear()
        assert t.send(upload()).status == 200
    post = cam.seen[-1]
    assert post[:2] == ("POST", "/up") and post[3] == b"abcd"
    assert [m for m, _, _, _ in cam.seen].count("POST") == 1


def test_preflight_challenge_round_trip_happens_once_per_upload_when_stale() -> None:
    cam = Camera()
    with SyncTransport(cfg(), transport=httpx.MockTransport(cam)) as t:
        t.send(upload())
        t.send(upload())
    assert cam.paths.count(("POST", "/up")) == 2


def test_replayable_body_needs_no_preflight() -> None:
    cam = Camera()
    with SyncTransport(cfg(), transport=httpx.MockTransport(cam)) as t:
        t.send(Request("POST", "/up", body=RawBody(b"abc", "application/octet-stream")))
    assert cam.paths == [("POST", "/up"), ("POST", "/up")]


def test_wrong_password_fails_before_the_body_is_sent() -> None:
    cam = Camera(password="other")
    with SyncTransport(cfg(), transport=httpx.MockTransport(cam)) as t, pytest.raises(AuthError):
        t.send(upload())
    assert all(p == PREFLIGHT_PATH for _, p in cam.paths)


def test_unverifiable_preflight_answer_fails_before_the_body_is_sent() -> None:
    cam = Camera(preflight_status=403)
    with SyncTransport(cfg(), transport=httpx.MockTransport(cam)) as t, pytest.raises(AuthError, match="HTTP 403"):
        t.send(upload())
    assert ("POST", "/up") not in cam.paths


def test_anonymous_device_streams_directly() -> None:
    cam = Camera()
    seen: list[str] = []

    def open_device(request: httpx.Request) -> httpx.Response:
        seen.append(request.url.path)
        return httpx.Response(200)

    with SyncTransport(ConnectionConfig("cam"), transport=httpx.MockTransport(open_device)) as t:
        t.send(upload())
    assert seen == ["/up"] and not cam.seen


def test_base_path_applies_to_the_preflight() -> None:
    cam = Camera()
    config = ConnectionConfig("cam", credentials=Credentials("root", "pw"), base_path="/prefix")
    with SyncTransport(config, transport=httpx.MockTransport(cam)) as t:
        t.send(upload())
    assert cam.paths[0] == ("GET", "/prefix" + PREFLIGHT_PATH)


@pytest.mark.anyio
async def test_async_streamed_upload_verifies_first() -> None:
    cam = Camera()

    async with AsyncTransport(cfg(), transport=httpx.MockTransport(cam)) as t:
        assert (await t.send(upload())).status == 200
    assert cam.paths == [("GET", PREFLIGHT_PATH), ("GET", PREFLIGHT_PATH), ("POST", "/up")]


@pytest.mark.anyio
async def test_async_wrong_password_fails_before_the_body_is_sent() -> None:
    cam = Camera(password="other")
    async with AsyncTransport(cfg(), transport=httpx.MockTransport(cam)) as t:
        with pytest.raises(AuthError):
            await t.send(upload())
    assert ("POST", "/up") not in cam.paths


@pytest.mark.parametrize("status", [403, 500])
def test_failed_preflight_with_cached_credentials_does_not_send_the_body(status: int) -> None:
    cam = Camera()
    with SyncTransport(cfg(), transport=httpx.MockTransport(cam)) as t:
        t.send(Request("GET", "/other"))  # credentials are now verified
        cam.preflight_status = status
        cam.seen.clear()
        with pytest.raises(AuthError, match=f"HTTP {status}"):
            t.send(upload())
    assert ("POST", "/up") not in cam.paths


@pytest.mark.anyio
@pytest.mark.parametrize("status", [403, 500])
async def test_async_failed_preflight_with_cached_credentials_does_not_send_the_body(status: int) -> None:
    cam = Camera()
    async with AsyncTransport(cfg(), transport=httpx.MockTransport(cam)) as t:
        await t.send(Request("GET", "/other"))
        cam.preflight_status = status
        cam.seen.clear()
        with pytest.raises(AuthError, match=f"HTTP {status}"):
            await t.send(upload())
    assert ("POST", "/up") not in cam.paths
