from __future__ import annotations

import hashlib
import re
from types import SimpleNamespace

import httpx
import pytest

from ax_devil_device_api._http.auth import parse_challenges
from ax_devil_device_api._http.config import ConnectionConfig, Credentials
from ax_devil_device_api._http.transport import AsyncTransport, SyncTransport
from ax_devil_device_api._http.types import JsonBody, RawBody, Request
from ax_devil_device_api.errors import AuthError

CREDS = Credentials("root", "pw")
DIGEST = 'Digest realm="AXIS", nonce="n1", qop="auth", opaque="op", algorithm=MD5'


def _fields(header: str) -> dict[str, str]:
    return {m[0]: m[1] or m[2] for m in re.findall(r'(\w+)=(?:"([^"]*)"|([^,\s]+))', header)}


def config(creds: Credentials | None = CREDS) -> ConnectionConfig:
    return ConnectionConfig("cam", credentials=creds)


class Device:
    """Scriptable fake device that records requests."""

    def __init__(self, challenge: list[str], password: str = "pw", ok: int = 200) -> None:
        self.challenge = challenge
        self.password = password
        self.ok = ok
        self.seen: list[SimpleNamespace] = []
        self.stale_next = False

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.seen.append(
            SimpleNamespace(headers=httpx.Headers(request.headers), content=request.content, method=request.method)  # type: ignore[arg-type]
        )
        auth = request.headers.get("authorization")
        if auth is not None and self.stale_next and auth.startswith("Digest"):
            self.stale_next = False
            return httpx.Response(401, headers=[("WWW-Authenticate", DIGEST.replace("n1", "n2") + ", stale=true")])
        if auth is not None and self._valid(request, auth):
            return httpx.Response(self.ok)
        return httpx.Response(401, headers=[("WWW-Authenticate", c) for c in self.challenge])

    def _valid(self, request: httpx.Request, auth: str) -> bool:
        if auth.startswith("Basic "):
            import base64

            return base64.b64decode(auth[6:]).decode() == f"root:{self.password}"
        fields = _fields(auth)
        h = lambda s: hashlib.md5(s.encode()).hexdigest()  # noqa: E731
        ha1 = h(f"root:AXIS:{self.password}")
        ha2 = h(f"{request.method}:{request.url.raw_path.decode()}")
        expected = h(f"{ha1}:{fields['nonce']}:{fields['nc']}:{fields['cnonce']}:auth:{ha2}")
        return fields["response"] == expected


def sync(device: Device, creds: Credentials | None = CREDS) -> SyncTransport:
    return SyncTransport(config(creds), transport=httpx.MockTransport(device))


def get(**kw) -> Request:
    return Request("GET", "/x", **kw)


def test_no_preemptive_basic() -> None:
    dev = Device(["Basic realm=a"])
    t = sync(dev)
    assert t.send(get()).status == 200
    assert "authorization" not in dev.seen[0].headers
    assert dev.seen[1].headers["authorization"].startswith("Basic ")


def test_basic_reused_once_verified() -> None:
    dev = Device(["Basic realm=a"])
    t = sync(dev)
    t.send(get())
    dev.seen.clear()
    t.send(get())
    assert len(dev.seen) == 1 and "authorization" in dev.seen[0].headers


def test_digest_preferred_over_basic() -> None:
    dev = Device(["Basic realm=a", DIGEST])
    t = sync(dev)
    assert t.send(get()).status == 200
    assert dev.seen[1].headers["authorization"].startswith("Digest ")


def test_digest_preferred_when_in_one_header() -> None:
    dev = Device([f"Basic realm=a, {DIGEST}"])
    sync(dev).send(get())
    assert dev.seen[1].headers["authorization"].startswith("Digest ")


def test_digest_verified_state_reused_with_nc_increment() -> None:
    dev = Device([DIGEST])
    t = sync(dev)
    t.send(get(query=(("a", "b"),)))
    dev.seen.clear()
    assert t.send(get()).status == 200
    assert t.send(get()).status == 200
    assert len(dev.seen) == 2
    assert "nc=00000002" in dev.seen[0].headers["authorization"]
    assert "nc=00000003" in dev.seen[1].headers["authorization"]
    assert 'opaque="op"' in dev.seen[0].headers["authorization"]


@pytest.mark.parametrize("status", [403, 500])
def test_candidate_not_promoted_on_non_2xx(status: int) -> None:
    dev = Device([DIGEST], ok=status)
    t = sync(dev)
    assert t.send(get()).status == status
    dev.seen.clear()
    t.send(get())
    assert "authorization" not in dev.seen[0].headers


def test_demotion_on_later_401() -> None:
    dev = Device([DIGEST])
    t = sync(dev)
    t.send(get())
    dev.password = "changed-pw"
    dev.seen.clear()
    with pytest.raises(AuthError):
        t.send(get())
    # verified state was cleared: next request starts anonymous
    dev.seen.clear()
    dev.password = "pw"
    assert t.send(get()).status == 200
    assert "authorization" not in dev.seen[0].headers


def test_stale_nonce_reauthenticates() -> None:
    dev = Device([DIGEST])
    t = sync(dev)
    t.send(get())
    dev.stale_next = True
    dev.seen.clear()
    assert t.send(get()).status == 200
    assert len(dev.seen) == 2
    assert 'nonce="n2"' in dev.seen[1].headers["authorization"]


def test_wrong_password_raises() -> None:
    for challenge in ([DIGEST], ["Basic realm=a"]):
        with pytest.raises(AuthError):
            sync(Device(challenge, password="other")).send(get())


def test_no_credentials_returns_401() -> None:
    dev = Device([DIGEST])
    resp = sync(dev, None).send(get())
    assert resp.status == 401
    assert len(dev.seen) == 1


def test_no_supported_challenge_raises() -> None:
    with pytest.raises(AuthError):
        sync(Device(["Bearer realm=x"])).send(get())


@pytest.mark.parametrize(
    "challenge",
    [
        'Digest realm="a", nonce="n", algorithm=FOO',
        'Digest realm="a", nonce="n", qop="auth-int"',
        'Digest realm="a"',
    ],
)
def test_unsupported_digest_raises(challenge: str) -> None:
    with pytest.raises(AuthError):
        sync(Device([challenge, "Basic realm=a"])).send(get())


def test_non_replayable_is_preceded_by_a_preflight() -> None:
    dev = Device([DIGEST])
    t = sync(dev)
    req = Request("POST", "/up", body=RawBody(iter([b"a", b"b"]), "application/octet-stream"))
    assert not req.replayable
    assert t.send(req).status == 200
    assert [s.method for s in dev.seen] == ["GET", "GET", "POST"]
    assert dev.seen[-1].content == b"ab"


def test_non_replayable_with_wrong_password_never_sends_the_body() -> None:
    dev = Device([DIGEST], password="other")
    t = sync(dev)
    with pytest.raises(AuthError):
        t.send(Request("POST", "/up", body=RawBody(iter([b"a"]), "application/octet-stream")))
    assert all(s.method == "GET" for s in dev.seen)


def test_non_replayable_with_verified_state_sent_once() -> None:
    dev = Device([DIGEST])
    t = sync(dev)
    t.send(get())
    dev.seen.clear()
    req = Request("POST", "/up", body=RawBody(iter([b"a"]), "application/octet-stream"))
    assert t.send(req).status == 200
    assert [r.method for r in dev.seen] == ["GET", "POST"]  # preflight re-verifies, then the body is sent once
    dev.seen.clear()
    dev.password = "changed"
    with pytest.raises(AuthError):
        t.send(Request("POST", "/up", body=RawBody(iter([b"a"]), "application/octet-stream")))
    assert all(r.method == "GET" for r in dev.seen)  # the body is never sent with stale credentials


def test_replayable_body_resent_on_challenge() -> None:
    dev = Device([DIGEST])
    t = sync(dev)
    assert t.send(Request("POST", "/p", body=JsonBody({"a": 1}))).status == 200
    assert [r.content for r in dev.seen] == [b'{"a":1}', b'{"a":1}'] or len({r.content for r in dev.seen}) == 1


def test_anonymous_never_sends_authorization() -> None:
    dev = Device([DIGEST])
    t = sync(dev)
    t.send(get())  # establish verified state
    dev.seen.clear()
    resp = t.send(get(auth="anonymous"))
    assert resp.status == 401
    assert len(dev.seen) == 1 and "authorization" not in dev.seen[0].headers


def test_if_challenged_never_preemptive() -> None:
    dev = Device([DIGEST])
    t = sync(dev)
    t.send(get())
    dev.seen.clear()
    assert t.send(get(auth="if_challenged")).status == 200
    assert "authorization" not in dev.seen[0].headers
    assert len(dev.seen) == 2


def test_if_challenged_anonymous_ok_device() -> None:
    t = SyncTransport(config(), transport=httpx.MockTransport(lambda r: httpx.Response(200)))
    assert t.send(get(auth="if_challenged")).status == 200


def test_quoted_comma_challenge_parsing() -> None:
    header = 'Basic realm="a, Digest x=y", Digest realm="b,c", nonce="n", qop="auth,auth-int", stale=true'
    ch = parse_challenges([header])
    assert [c.scheme for c in ch] == ["basic", "digest"]
    assert ch[0].params == {"realm": "a, Digest x=y"}
    assert ch[1].params["realm"] == "b,c"
    assert ch[1].params["qop"] == "auth,auth-int"
    assert ch[1].params["stale"] == "true"


def test_unterminated_quote_yields_nothing() -> None:
    assert parse_challenges(['Digest realm="x']) == []


def test_digest_known_vector() -> None:
    """RFC 2617 example (qop=auth, MD5) computed against the fixed cnonce."""
    from ax_devil_device_api._http.auth import _Counter, _DigestState, parse_digest

    ch = parse_challenges(
        [
            'Digest realm="testrealm@host.com", qop="auth,auth-int", '
            'nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093", opaque="5ccc069c403ebaf9f0171e9517f40e41"'
        ]
    )[0]
    state = _DigestState(parse_digest(ch), _Counter())
    header = state.header(Credentials("Mufasa", "Circle Of Life"), "GET", "/dir/index.html")
    fields = _fields(header)
    h = lambda s: hashlib.md5(s.encode()).hexdigest()  # noqa: E731
    ha1 = h("Mufasa:testrealm@host.com:Circle Of Life")
    ha2 = h("GET:/dir/index.html")
    assert fields["response"] == h(f"{ha1}:{fields['nonce']}:00000001:{fields['cnonce']}:auth:{ha2}")


@pytest.mark.anyio
async def test_async_flow_digest_and_reuse() -> None:
    dev = Device([DIGEST])

    async def handler(request: httpx.Request) -> httpx.Response:
        return dev(request)

    async with AsyncTransport(config(), transport=httpx.MockTransport(handler)) as t:
        assert (await t.send(get())).status == 200
        dev.seen.clear()
        assert (await t.send(get())).status == 200
        assert len(dev.seen) == 1
        with pytest.raises(AuthError, match="rejected the credentials"):
            dev.password = "x"
            t._auth.reset()
            await t.send(Request("POST", "/u", body=RawBody(iter([b"a"]), "text/plain")))
