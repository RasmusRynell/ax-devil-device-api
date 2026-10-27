"""Credentials that would break or inject into a header are reported, never stripped; the message never holds the secret."""

from __future__ import annotations

import io
from typing import Any

import httpx
import pytest

from ax_devil_device_api import cli
from ax_devil_device_api._http.config import BearerToken, ConnectionConfig, Credentials
from ax_devil_device_api._http.transport import AsyncTransport, SyncTransport
from ax_devil_device_api._http.types import Request
from ax_devil_device_api.errors import ConfigurationError
from ax_devil_device_api.testing import MockCamera

SECRET = "s3cret-token-value"
BAD = [SECRET + "\n", SECRET + "\r\n", "abc\ndef", "abc\rdef", "abc\x00def", "abc\x7fdef", "abc\x1bdef", "abc\x85def"]


def _ok(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, text="ok")


@pytest.mark.parametrize("token", BAD)
def test_static_bearer_token_with_a_control_character_is_rejected_without_echoing_it(token: str) -> None:
    with pytest.raises(ConfigurationError, match="control character") as info:
        BearerToken(token)
    assert token not in str(info.value) and SECRET not in str(info.value)


def test_clean_bearer_tokens_pass_and_are_not_modified() -> None:
    assert BearerToken("abc.DEF-123_~+/=").current() == "abc.DEF-123_~+/="
    assert BearerToken(lambda: "fresh").current() == "fresh"


@pytest.mark.parametrize("token", BAD)
def test_callable_bearer_token_is_checked_when_it_is_used(token: str) -> None:
    provider = BearerToken(lambda: token)  # constructing is fine: the value is not known yet
    with pytest.raises(ConfigurationError, match="control character") as info:
        provider.current()
    assert SECRET not in str(info.value)


@pytest.mark.parametrize("token", BAD[:3])
def test_sync_request_with_a_bad_callable_token_is_a_configuration_error(token: str) -> None:
    config = ConnectionConfig("cam", credentials=BearerToken(lambda: token))
    with SyncTransport(config, transport=httpx.MockTransport(_ok)) as transport:
        with pytest.raises(ConfigurationError, match="control character") as info:
            transport.send(Request("GET", "/x"))
    assert SECRET not in str(info.value)


@pytest.mark.anyio
@pytest.mark.parametrize("token", BAD[:3])
async def test_async_request_with_a_bad_callable_token_is_a_configuration_error(token: str) -> None:
    config = ConnectionConfig("cam", credentials=BearerToken(lambda: token))
    async with AsyncTransport(config, transport=httpx.MockTransport(_ok)) as transport:
        with pytest.raises(ConfigurationError, match="control character") as info:
            await transport.send(Request("GET", "/x"))
    assert SECRET not in str(info.value)


def test_a_provider_that_starts_clean_and_turns_bad_is_caught_on_the_later_request() -> None:
    values = iter(["good", "bad\n"])
    config = ConnectionConfig("cam", credentials=BearerToken(lambda: next(values)))
    with SyncTransport(config, transport=httpx.MockTransport(_ok)) as transport:
        assert transport.send(Request("GET", "/x")).status == 200
        with pytest.raises(ConfigurationError):
            transport.send(Request("GET", "/x"))


@pytest.mark.parametrize("bad", BAD)
def test_basic_and_digest_usernames_and_passwords_reject_control_characters(bad: str) -> None:
    for username, password in ((bad, "pw"), ("root", bad)):
        with pytest.raises(ConfigurationError, match="control character") as info:
            Credentials(username, password)
        assert SECRET not in str(info.value)
    with pytest.raises(ConfigurationError):
        ConnectionConfig("cam", credentials=Credentials.from_pair(("root", bad)))


def test_clean_usernames_and_passwords_pass() -> None:
    assert Credentials("root", "p@ss word: ünï").password == "p@ss word: ünï"
    assert Credentials("root", "").password == ""


def test_non_string_credentials_do_not_echo_the_value() -> None:
    with pytest.raises(ConfigurationError) as info:
        Credentials("root", b"hunter2")  # type: ignore[arg-type]
    assert "hunter2" not in str(info.value) and "bytes" in str(info.value)


# --- the CLI closes the device it opens ------------------------------------------------------------------------------------


class _Tracked:
    """Wraps a Device so a test can see whether it was closed."""

    def __init__(self, device: Any) -> None:
        self.device = device
        self.closed = 0

    def __getattr__(self, name: str) -> Any:
        return getattr(self.device, name)

    def __enter__(self) -> Any:
        return self.device.__enter__()

    def __exit__(self, *exc: object) -> None:
        self.closed += 1
        self.device.__exit__(*exc)


@pytest.mark.parametrize("command", [["apis", "--supported"], ["supported"], ["summary"]])
def test_every_device_command_closes_its_device(monkeypatch: pytest.MonkeyPatch, command: list[str]) -> None:
    cam = MockCamera()
    cam.identity(model="AXIS X", firmware="11.0.0")
    cam.api_list({"mqtt-client": "1.0"})
    made: list[_Tracked] = []

    def factory(args: Any) -> _Tracked:
        tracked = _Tracked(cam.device())
        made.append(tracked)
        return tracked

    monkeypatch.setattr(cli, "make_device", factory)
    out, err = io.StringIO(), io.StringIO()
    cli.main(command, out=out, err=err)
    assert len(made) == 1 and made[0].closed == 1
