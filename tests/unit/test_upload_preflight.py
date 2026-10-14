"""Streamed (non-replayable) bodies verify the credentials with a preflight GET first."""

from __future__ import annotations

import hashlib
import re
from typing import Any

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


class FlakyPreflight(Camera):
    """Refuses the first connection to the preflight path, then behaves like the camera."""

    def __init__(self) -> None:
        super().__init__()
        self.refused = False

    def __call__(self, request: httpx.Request) -> httpx.Response:
        if request.url.path == PREFLIGHT_PATH and not self.refused:
            self.refused = True
            raise httpx.ConnectError("refused", request=request)
        return super().__call__(request)


def _one_shot_flow(request: Request):  # type: ignore[no-untyped-def]
    response = yield request
    return response.status


def test_transient_preflight_failure_is_retried_and_the_upload_sent_once() -> None:
    from ax_devil_device_api._http.options import RetryPolicy
    from ax_devil_device_api._runtime.driver import Call, run_sync

    cam = FlakyPreflight()
    call = Call(label=("a", "b"), retry=RetryPolicy(backoff=0))
    with SyncTransport(cfg(), transport=httpx.MockTransport(cam)) as t:
        assert run_sync(t, _one_shot_flow(upload()), call) == 200
    assert [p for p in cam.paths if p[0] == "POST"] == [("POST", "/up")]


@pytest.mark.anyio
async def test_async_transient_preflight_failure_is_retried_and_the_upload_sent_once() -> None:
    from ax_devil_device_api._http.options import RetryPolicy
    from ax_devil_device_api._runtime.driver import Call, run_async

    cam = FlakyPreflight()
    call = Call(label=("a", "b"), retry=RetryPolicy(backoff=0))
    async with AsyncTransport(cfg(), transport=httpx.MockTransport(cam)) as t:
        assert await run_async(t, _one_shot_flow(upload()), call) == 200
    assert [p for p in cam.paths if p[0] == "POST"] == [("POST", "/up")]


def test_a_failure_while_sending_the_body_is_still_not_retried() -> None:
    from ax_devil_device_api._http.options import RetryPolicy
    from ax_devil_device_api._runtime.driver import Call, run_sync
    from ax_devil_device_api.errors import TransportError

    class BodyFails(Camera):
        def __call__(self, request: httpx.Request) -> httpx.Response:
            if request.method == "POST":
                raise httpx.ConnectError("refused", request=request)
            return super().__call__(request)

    cam = BodyFails()
    call = Call(label=("a", "b"), retry=RetryPolicy(backoff=0))
    with SyncTransport(cfg(), transport=httpx.MockTransport(cam)) as t:
        with pytest.raises(TransportError):
            run_sync(t, _one_shot_flow(upload()), call)


# --- a stale nonce must not demote the verified credential; a demotion before the body is retried ---------------------------


class StaleCamera(Camera):
    """Answers one authorized GET /other with a stale-nonce challenge, noting the auth state it sees on the retry."""

    def __init__(self) -> None:
        super().__init__()
        self.stale_next = False
        self.state_probe: Any = None
        self.state_on_retry: list[bool] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        if request.url.path == "/other" and "authorization" in request.headers:
            if self.stale_next:
                self.stale_next = False
                return httpx.Response(401, headers={"WWW-Authenticate": CHALLENGE + ", stale=true"})
            if self.state_probe is not None:
                self.state_on_retry.append(self.state_probe())
        return super().__call__(request)


def test_stale_nonce_keeps_the_verified_state_while_the_request_is_retried() -> None:
    cam = StaleCamera()
    with SyncTransport(cfg(), transport=httpx.MockTransport(cam)) as t:
        t.send(Request("GET", "/other"))  # verified now
        cam.stale_next = True
        cam.state_probe = lambda: t._auth.has_verified_state
        assert t.send(Request("GET", "/other")).status == 200
        assert cam.state_on_retry and all(cam.state_on_retry)
        assert t._auth.has_verified_state


@pytest.mark.anyio
async def test_async_stale_nonce_keeps_the_verified_state_while_the_request_is_retried() -> None:
    cam = StaleCamera()
    async with AsyncTransport(cfg(), transport=httpx.MockTransport(cam)) as t:
        await t.send(Request("GET", "/other"))
        cam.stale_next = True
        cam.state_probe = lambda: t._auth.has_verified_state
        assert (await t.send(Request("GET", "/other"))).status == 200
        assert cam.state_on_retry and all(cam.state_on_retry)


def test_a_genuine_rejection_still_demotes() -> None:
    cam = StaleCamera()
    with SyncTransport(cfg(), transport=httpx.MockTransport(cam)) as t:
        t.send(Request("GET", "/other"))
        cam.password = "changed"
        with pytest.raises(AuthError):
            t.send(Request("GET", "/other"))
        assert not t._auth.has_verified_state


def test_upload_demoted_after_the_preflight_is_reverified_and_sent_once() -> None:
    cam = Camera()
    demoted: list[bool] = []

    class Racing(SyncTransport):
        def _send_once(self, request: Request, *, stream: bool) -> Any:
            if request.path == "/up" and not demoted:
                demoted.append(True)
                self._auth.reset()  # another request lost the verified state right after the preflight
            return super()._send_once(request, stream=stream)

    with Racing(cfg(), transport=httpx.MockTransport(cam)) as t:
        assert t.send(upload()).status == 200
    assert [p for p in cam.paths if p[0] == "POST"] == [("POST", "/up")]
    assert [p for p in cam.paths if p[1] == PREFLIGHT_PATH and p[0] == "GET"]


@pytest.mark.anyio
async def test_async_upload_demoted_after_the_preflight_is_reverified_and_sent_once() -> None:
    cam = Camera()
    demoted: list[bool] = []

    class Racing(AsyncTransport):
        async def _send_once(self, request: Request, *, stream: bool) -> Any:
            if request.path == "/up" and not demoted:
                demoted.append(True)
                self._auth.reset()
            return await super()._send_once(request, stream=stream)

    async with Racing(cfg(), transport=httpx.MockTransport(cam)) as t:
        assert (await t.send(upload())).status == 200
    assert [p for p in cam.paths if p[0] == "POST"] == [("POST", "/up")]
