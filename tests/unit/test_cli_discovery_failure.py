"""``supported`` and ``apis --supported`` report why discovery failed instead of listing every API as unknown."""

from __future__ import annotations

import io
import json
import time
from typing import Any

import httpx
import pytest

from ax_devil_device_api import AsyncDevice, Device, Support, cli
from ax_devil_device_api.features import async_api_support, load_all
from ax_devil_device_api.testing import MockCamera


def run(*argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    code = cli.main(list(argv), out=out, err=err)
    return code, out.getvalue(), err.getvalue()


def _counting(handler: Any) -> tuple[httpx.MockTransport, list[str]]:
    seen: list[str] = []

    def wrapped(request: httpx.Request) -> httpx.Response:
        seen.append(request.url.path)
        return handler(request)

    return httpx.MockTransport(wrapped), seen


def _refused(request: httpx.Request) -> httpx.Response:
    raise httpx.ConnectError("refused", request=request)


def _unauthorized(request: httpx.Request) -> httpx.Response:
    return httpx.Response(401, headers={"WWW-Authenticate": 'Digest realm="AXIS", nonce="n", qop="auth"'}, text="no")


@pytest.mark.parametrize("command", [["supported"], ["apis", "--supported"]])
def test_a_closed_port_exits_1_with_the_cause_and_finishes_quickly(command: list[str]) -> None:
    started = time.monotonic()
    code, out, err = run("--host", "127.0.0.1", "--port", "1", "--http", "--user", "u", "--password", "p", "--timeout", "5", *command)
    assert time.monotonic() - started < 10
    assert code == 1 and out == ""
    error = json.loads(err.splitlines()[-1])["error"]
    assert error["type"] in {"ConnectionFailed", "ConnectTimeout"} and error["probes"]


@pytest.mark.parametrize("command", [["supported"], ["apis", "--supported"]])
def test_401_everywhere_exits_1_with_an_auth_error(monkeypatch: pytest.MonkeyPatch, command: list[str]) -> None:
    transport, _ = _counting(_unauthorized)
    monkeypatch.setattr(cli, "make_device", lambda args: Device("cam", credentials=("u", "wrong"), transport=transport))
    code, out, err = run(*command)
    assert code == 1 and out == ""
    assert json.loads(err.splitlines()[-1])["error"]["type"] == "AuthError"


def test_partial_discovery_exits_0_and_lists_the_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    cam = MockCamera()
    cam.identity(model="AXIS X", firmware="11.0.0")
    cam.api_list({"mqtt-client": "1.0"})
    monkeypatch.setattr(cli, "make_device", lambda args: cam.device())
    code, out, err = run("supported")
    payload = json.loads(out)
    assert code == 0 and payload["apis"]["mqtt_client"]["status"] == "yes"
    assert payload["errors"], "probes that could not run are listed, not dropped"
    assert all(json.loads(line)["warning"]["message"] for line in err.splitlines())
    code, out, err = run("apis", "--supported")
    assert code == 0 and "mqtt_client" in {a["name"] for a in json.loads(out)} and err


def test_sync_discovery_stops_probing_after_the_device_proves_unreachable() -> None:
    transport, seen = _counting(_refused)
    with Device("cam", credentials=("u", "p"), transport=transport) as dev:
        results = dev.supports_many([entry.sync_class for entry in load_all()])
        first = len(seen)
        assert first <= 4, f"{first} requests: the other probes should have been skipped"
        assert all(r.status is Support.UNKNOWN for r in results.values())
        assert any("not run" in e for r in results.values() for e in r.errors)
        # failed probes are not cached: a later call asks again (and is cut short again)
        dev.supports_many([entry.sync_class for entry in load_all()])
        assert len(seen) > first


@pytest.mark.anyio
async def test_async_discovery_stops_probing_after_the_device_proves_unreachable() -> None:
    transport, seen = _counting(_refused)
    async with AsyncDevice("cam", credentials=("u", "p"), transport=transport, max_concurrency=1) as dev:
        results = await async_api_support(dev)
        assert len(seen) <= 4, f"{len(seen)} requests: the other probes should have been skipped"
        assert all(r.status is Support.UNKNOWN for r in results.values())
        assert any("not run" in e for r in results.values() for e in r.errors)


def test_sync_auth_failure_also_short_circuits() -> None:
    transport, seen = _counting(_unauthorized)
    with Device("cam", credentials=("u", "wrong"), transport=transport) as dev:
        dev.supports_many([entry.sync_class for entry in load_all()])
    assert len(seen) <= 10
