from __future__ import annotations

import asyncio
import ssl
import threading
import time

import httpx
import pytest

from ax_devil_device_api import errors
from ax_devil_device_api._http.config import BearerToken, ConnectionConfig, Credentials
from ax_devil_device_api._http.transport import AsyncTransport, SyncTransport
from ax_devil_device_api._http.types import (
    FilePart,
    FormBody,
    JsonBody,
    MultipartBody,
    RawBody,
    Request,
)


def cfg(**kw) -> ConnectionConfig:
    return ConnectionConfig("cam", **kw)


def make(handler, **kw) -> SyncTransport:
    return SyncTransport(cfg(**kw), transport=httpx.MockTransport(handler))


def capture():
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, content=b"ok", headers=[("X-A", "1"), ("X-A", "2")])

    return seen, handler


def test_get_has_no_content_type_or_accept() -> None:
    seen, h = capture()
    resp = make(h).send(Request("GET", "/a", query=(("k", "v"), ("k", "w"))))
    r = seen[0]
    assert "content-type" not in r.headers and "accept" not in r.headers
    assert r.headers["user-agent"] == "ax-devil-device-api/1.0"
    assert str(r.url) == "https://cam/a?k=v&k=w"
    assert resp.status == 200 and resp.content == b"ok"
    assert resp.headers.get_all("x-a") == ["1", "2"]
    assert resp.request.path == "/a"


def test_accept_and_extra_headers() -> None:
    seen, h = capture()
    make(h).send(Request("GET", "/a", accept="application/json", headers=(("X-Y", "z"),)))
    assert seen[0].headers["accept"] == "application/json" and seen[0].headers["x-y"] == "z"


def test_json_body() -> None:
    seen, h = capture()
    make(h).send(Request("POST", "/a", body=JsonBody({"a": 1})))
    assert seen[0].headers["content-type"] == "application/json"
    assert b'"a"' in seen[0].content


def test_form_body() -> None:
    seen, h = capture()
    make(h).send(Request("POST", "/a", body=FormBody((("a", "1"), ("a", "2 3")))))
    assert seen[0].headers["content-type"] == "application/x-www-form-urlencoded"
    assert seen[0].content == b"a=1&a=2+3"


def test_raw_body() -> None:
    seen, h = capture()
    make(h).send(Request("PUT", "/a", body=RawBody(b"xyz", "text/plain")))
    assert seen[0].headers["content-type"] == "text/plain" and seen[0].content == b"xyz"


def test_multipart_body() -> None:
    seen, h = capture()
    body = MultipartBody((("f", "v"),), (FilePart("file", "a.bin", b"DATA", "application/x-foo"),))
    make(h).send(Request("POST", "/a", body=body))
    assert seen[0].headers["content-type"].startswith("multipart/form-data; boundary=")
    assert b'name="f"' in seen[0].content and b'filename="a.bin"' in seen[0].content and b"DATA" in seen[0].content


def test_no_redirect_following() -> None:
    t = make(lambda r: httpx.Response(302, headers={"Location": "/b"}))
    assert t.send(Request("GET", "/a")).status == 302


def test_per_request_timeout() -> None:
    seen, h = capture()
    make(h).send(Request("GET", "/a", timeout=3.0))
    assert seen[0].extensions["timeout"]["read"] == 3.0
    make(h, timeout=7.0).send(Request("GET", "/a"))
    assert seen[1].extensions["timeout"]["read"] == 7.0


def test_stream_success() -> None:
    t = make(lambda r: httpx.Response(200, content=b"abcdef"))
    with t.open_stream(Request("GET", "/s", stream=True)) as (resp, chunks):
        assert resp.status == 200 and resp.content == b""
        assert b"".join(chunks) == b"abcdef"


def test_stream_non_2xx_reads_body() -> None:
    t = make(lambda r: httpx.Response(500, content=b"boom"))
    with t.open_stream(Request("GET", "/s", stream=True)) as (resp, chunks):
        assert resp.status == 500 and resp.content == b"boom"
        assert list(chunks) == []


def test_stream_closes_response() -> None:
    closed = []

    class Body(httpx.SyncByteStream):
        def __iter__(self):
            yield b"a"

        def close(self) -> None:
            closed.append(True)

    t = make(lambda r: httpx.Response(200, stream=Body()))
    with t.open_stream(Request("GET", "/s", stream=True)):
        pass
    assert closed


@pytest.mark.parametrize(
    ("exc", "expected", "sent"),
    [
        (httpx.ConnectTimeout("t"), errors.ConnectTimeout, False),
        (httpx.ReadTimeout("t"), errors.ReadTimeout, True),
        (httpx.WriteTimeout("t"), errors.WriteTimeout, True),
        (httpx.PoolTimeout("t"), errors.PoolTimeout, False),
        (httpx.ConnectError("refused"), errors.ConnectionFailed, False),
        (httpx.ReadError("reset"), errors.ConnectionFailed, True),
        (httpx.WriteError("reset"), errors.ConnectionFailed, True),
        (httpx.RemoteProtocolError("bad"), errors.ConnectionFailed, True),
        (httpx.ConnectError("[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed"), errors.TlsError, False),
    ],
)
def test_exception_mapping(exc: Exception, expected: type, sent: bool) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise exc

    t = make(handler)
    with pytest.raises(expected) as info:
        t.send(Request("GET", "/a"))
    assert info.value.__cause__ is None and info.value.__context__ is None  # the httpx exception (and its request) is not chained
    assert type(exc).__name__ in str(info.value)  # but its class name stays in the text
    assert info.value.request_sent is sent
    assert type(info.value) is expected
    with pytest.raises(expected) as info2:
        with t.open_stream(Request("GET", "/a", stream=True)):
            pass
    assert info2.value.request_sent is sent


def test_exception_while_iterating_stream() -> None:
    class Body(httpx.SyncByteStream):
        def __iter__(self):
            yield b"a"
            raise httpx.ReadTimeout("stalled")

    t = make(lambda r: httpx.Response(200, stream=Body()))
    with pytest.raises(errors.ReadTimeout) as info:
        with t.open_stream(Request("GET", "/s", stream=True)) as (_, chunks):
            list(chunks)
    assert info.value.__cause__ is None and info.value.__context__ is None and "stalled" in str(info.value)


def test_tls_error_via_cause() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        try:
            raise ssl.SSLError("handshake")
        except ssl.SSLError as e:
            raise httpx.ConnectError("failed") from e

    with pytest.raises(errors.TlsError):
        make(handler).send(Request("GET", "/a"))


def test_debug_hook_redacts_secrets() -> None:
    events: list[dict] = []
    seen, h = capture()
    t = make(h, credentials=Credentials("root", "hunter2"), on_request=events.append, verify=False)
    t.send(
        Request(
            "POST",
            "/a",
            query=(("apikey", "SECRET1"), ("n", "1")),
            body=JsonBody({"password": "SECRET2", "ok": "yes", "nested": {"token": "SECRET3"}}),
            headers=(("Authorization", "Bearer SECRET4"), ("X-Ok", "fine")),
        )
    )
    text = repr(events)
    for secret in ("SECRET1", "SECRET2", "SECRET3", "SECRET4", "hunter2"):
        assert secret not in text
    ev = events[0]
    assert ev["request"]["method"] == "POST" and ev["request"]["url"] == "https://cam/a"
    assert ev["request"]["headers"]["X-Ok"] == "fine"
    assert ["n", "1"] in ev["request"]["query"]
    assert ev["settings"] == {"timeout": 10.0, "ssl_verify": False}


def test_debug_form_and_url_redaction() -> None:
    from ax_devil_device_api._http.debug import redact_url

    events: list[dict] = []
    make(capture()[1], on_request=events.append).send(
        Request("POST", "/a", body=FormBody((("pwd", "SECRET"), ("a", "b"))))
    )
    assert "SECRET" not in repr(events)
    assert redact_url("https://u:p@h:8/x?token=abc&y=1") == "https://<redacted>@h:8/x?token=%3Credacted%3E&y=1"


@pytest.mark.anyio
async def test_async_send_and_stream() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/bad":
            return httpx.Response(404, content=b"nope")
        return httpx.Response(200, content=b"abc")

    async with AsyncTransport(cfg(), transport=httpx.MockTransport(handler)) as t:
        assert (await t.send(Request("GET", "/ok"))).content == b"abc"
        async with t.open_stream(Request("GET", "/ok", stream=True)) as (resp, chunks):
            assert resp.content == b"" and b"".join([c async for c in chunks]) == b"abc"
        async with t.open_stream(Request("GET", "/bad", stream=True)) as (resp, chunks):
            assert resp.status == 404 and resp.content == b"nope"
            assert [c async for c in chunks] == []


@pytest.mark.anyio
async def test_async_exception_mapping() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("t")

    async with AsyncTransport(cfg(), transport=httpx.MockTransport(handler)) as t:
        with pytest.raises(errors.ConnectTimeout):
            await t.send(Request("GET", "/a"))
        with pytest.raises(errors.ConnectTimeout):
            async with t.open_stream(Request("GET", "/a", stream=True)):
                pass


def test_base_path_prefix_and_debug_url() -> None:
    seen, h = capture()
    events: list[dict] = []
    t = make(h, base_path="/vms/cam1", on_request=events.append)
    t.send(Request("GET", "/a", query=(("k", "v"),)))
    assert str(seen[0].url) == "https://cam/vms/cam1/a?k=v"
    assert events[0]["request"]["url"] == "https://cam/vms/cam1/a"


def test_digest_uri_includes_base_path() -> None:
    challenge = 'Digest realm="AXIS", nonce="n1", qop="auth", algorithm=MD5'
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if "authorization" not in request.headers:
            return httpx.Response(401, headers={"WWW-Authenticate": challenge})
        return httpx.Response(200)

    t = make(handler, base_path="/p", credentials=Credentials("root", "pw"))
    assert t.send(Request("GET", "/a", query=(("x", "1"),))).status == 200
    assert 'uri="/p/a?x=1"' in seen[1].headers["authorization"]


def test_proxy_passed_to_client(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict = {}
    real = httpx.Client

    def fake(*args, **kwargs):
        captured.update(kwargs)
        kwargs.pop("proxy", None)
        return real(*args, **kwargs)

    monkeypatch.setattr(httpx, "Client", fake)
    SyncTransport(cfg(proxy="http://proxy:3128"))
    assert captured["proxy"] == "http://proxy:3128"
    captured.clear()
    SyncTransport(cfg(), transport=httpx.MockTransport(lambda r: httpx.Response(200)))
    assert "proxy" not in captured
    assert captured["limits"].max_connections == 6 and captured["limits"].max_keepalive_connections == 4


def test_bearer_static_and_debug_redaction() -> None:
    seen, h = capture()
    events: list[dict] = []
    t = make(h, credentials=BearerToken("TOK1"), on_request=events.append)
    t.send(Request("GET", "/a"))
    t.send(Request("GET", "/a", auth="if_challenged"))
    t.send(Request("GET", "/a", auth="anonymous"))
    assert seen[0].headers["authorization"] == "Bearer TOK1"
    assert "authorization" not in seen[1].headers  # if_challenged is never pre-emptive
    assert "authorization" not in seen[2].headers
    assert "TOK1" not in repr(events)
    t.send(Request("GET", "/a", headers=(("Authorization", "Bearer TOK2"),), auth="anonymous"))
    assert "TOK2" not in repr(events)


def test_bearer_static_401_raises_auth_error() -> None:
    n = []

    def h(request: httpx.Request) -> httpx.Response:
        n.append(1)
        return httpx.Response(401)

    with pytest.raises(errors.AuthError):
        make(h, credentials=BearerToken("T")).send(Request("GET", "/a"))
    assert len(n) == 1


def test_bearer_callable_refresh_on_401() -> None:
    tokens = iter(["old", "new", "newer"])
    seen: list[str] = []

    def h(request: httpx.Request) -> httpx.Response:
        seen.append(request.headers["authorization"])
        return httpx.Response(200 if request.headers["authorization"] == "Bearer new" else 401)

    t = make(h, credentials=BearerToken(lambda: next(tokens)))
    assert t.send(Request("GET", "/a")).status == 200
    assert seen == ["Bearer old", "Bearer new"]


def test_bearer_callable_still_401_and_non_replayable() -> None:
    calls = []

    def h(request: httpx.Request) -> httpx.Response:
        calls.append(1)
        return httpx.Response(401)

    t = make(h, credentials=BearerToken(lambda: "x"))
    with pytest.raises(errors.AuthError):
        t.send(Request("GET", "/a"))
    assert len(calls) == 2
    calls.clear()
    with pytest.raises(errors.AuthError):
        t.send(Request("PUT", "/a", body=RawBody(iter([b"a"]), "text/plain")))
    assert len(calls) == 1


def test_sync_concurrency_limit() -> None:
    state = {"now": 0, "max": 0}
    lock = threading.Lock()

    def h(request: httpx.Request) -> httpx.Response:
        with lock:
            state["now"] += 1
            state["max"] = max(state["max"], state["now"])
        time.sleep(0.05)
        with lock:
            state["now"] -= 1
        return httpx.Response(200)

    t = make(h, max_concurrency=1)
    threads = [threading.Thread(target=t.send, args=(Request("GET", "/a"),)) for _ in range(4)]
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    assert state["max"] == 1

    state["max"] = 0
    t = make(h, max_concurrency=2)
    threads = [threading.Thread(target=t.send, args=(Request("GET", "/a"),)) for _ in range(4)]
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    assert state["max"] == 2


def test_stream_slot_does_not_block_send_and_is_released() -> None:
    t = make(lambda r: httpx.Response(200, content=b"x"), max_concurrency=1, max_streams=1)
    with t.open_stream(Request("GET", "/s", stream=True)):
        assert t.send(Request("GET", "/a")).status == 200
        assert not t._stream_slots.acquire(blocking=False)
    with pytest.raises(RuntimeError):
        with t.open_stream(Request("GET", "/s", stream=True)):
            raise RuntimeError
    assert t._stream_slots.acquire(blocking=False)


@pytest.mark.anyio
async def test_async_concurrency_limit_and_stream_slot() -> None:
    state = {"now": 0, "max": 0}

    async def h(request: httpx.Request) -> httpx.Response:
        state["now"] += 1
        state["max"] = max(state["max"], state["now"])
        await asyncio.sleep(0.02)
        state["now"] -= 1
        return httpx.Response(200)

    t = AsyncTransport(cfg(max_concurrency=1, max_streams=1), transport=httpx.MockTransport(h))
    await asyncio.gather(*(t.send(Request("GET", "/a")) for _ in range(4)))
    assert state["max"] == 1
    async with t.open_stream(Request("GET", "/s", stream=True)):
        assert (await t.send(Request("GET", "/a"))).status == 200
    await t.aclose()


def test_async_transport_constructed_outside_loop() -> None:
    AsyncTransport(cfg(), transport=httpx.MockTransport(lambda r: httpx.Response(200)))
