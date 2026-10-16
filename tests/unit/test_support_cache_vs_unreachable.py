"""A cached answer survives a later connection failure; only APIs without evidence become unknown.

Discovery lists are any-of: one list that answered YES makes the API YES whatever the other lists said (a failed or
skipped probe only matters when no list said YES). A NO needs every list to have answered NO. So a cached DCA answer
decides ``oauth-ccgrant`` (its only list) even when the classic probe is refused, while ``mqtt-client`` (classic API
discovery) has no evidence and becomes UNKNOWN. Skipped probes are never cached, and never produce a cached NO.
"""

from __future__ import annotations

import httpx
import pytest

from ax_devil_device_api import AsyncDevice, Device, Support
from ax_devil_device_api.apis.mqtt_client import AsyncMqttClientApi, MqttClientApi
from ax_devil_device_api.apis.oauth_ccgrant import AsyncOauthCcgrantApi, OauthCcgrantApi


class Switch:
    """A device whose DCA discovery answers (or not) and that can drop off the network."""

    def __init__(self, dca: dict[str, dict[str, dict[str, object]]]) -> None:
        self.dca = dca
        self.refuse = False
        self.classic = False  # whether classic API discovery answers (it does not at first, so it is never cached)
        self.paths: list[str] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.paths.append(request.url.path)
        if self.refuse:
            raise httpx.ConnectError("refused", request=request)
        if request.url.path == "/config/discover":
            return httpx.Response(200, json={"apis": self.dca})
        if request.url.path == "/axis-cgi/apidiscovery.cgi" and self.classic:
            return httpx.Response(200, json={"data": {"apiList": [{"id": "mqtt-client", "version": "1.0"}]}})
        return httpx.Response(404, text="not found")


def sync_device(switch: Switch) -> Device:
    return Device("cam", credentials=("u", "p"), transport=httpx.MockTransport(switch))


def async_device(switch: Switch) -> AsyncDevice:
    return AsyncDevice("cam", credentials=("u", "p"), transport=httpx.MockTransport(switch), max_concurrency=1)  # serial probes: the flag is set before the later ones start


def test_sync_cached_dca_yes_survives_a_refused_classic_probe() -> None:
    switch = Switch({"oauth-ccgrant": {"v1": {}}})
    with sync_device(switch) as dev:
        assert dev.supports(OauthCcgrantApi).status is Support.YES  # the DCA answer is cached
        switch.refuse = True
        results = dev.supports_many([OauthCcgrantApi, MqttClientApi])
        assert results[OauthCcgrantApi].status is Support.YES
        assert results[MqttClientApi].status is Support.UNKNOWN and any("not run" in e or "ConnectionFailed" in e for e in results[MqttClientApi].errors)
        # nothing was cached from the failure: once the device is back the answer is real, not a remembered NO or unknown
        switch.refuse = False
        switch.classic = True
        assert dev.supports(MqttClientApi).status is Support.YES


def test_sync_cached_no_is_not_downgraded() -> None:
    switch = Switch({"something-else": {"v1": {}}})
    with sync_device(switch) as dev:
        assert dev.supports(OauthCcgrantApi).status is Support.NO
        switch.refuse = True
        assert dev.supports_many([OauthCcgrantApi])[OauthCcgrantApi].status is Support.NO
        assert dev.supports(OauthCcgrantApi).status is Support.NO


def test_sync_no_evidence_is_unknown_and_uncached() -> None:
    switch = Switch({"oauth-ccgrant": {"v1": {}}})
    switch.refuse = True
    with sync_device(switch) as dev:
        assert dev.supports(OauthCcgrantApi).status is Support.UNKNOWN
        switch.refuse = False
        assert dev.supports(OauthCcgrantApi).status is Support.YES  # the earlier failure left no cached verdict


@pytest.mark.anyio
async def test_async_cached_dca_yes_survives_a_refused_classic_probe() -> None:
    switch = Switch({"oauth-ccgrant": {"v1": {}}})
    async with async_device(switch) as dev:
        assert (await dev.supports(AsyncOauthCcgrantApi)).status is Support.YES
        switch.refuse = True
        results = await dev.supports_many([AsyncOauthCcgrantApi, AsyncMqttClientApi])
        assert results[AsyncOauthCcgrantApi].status is Support.YES
        assert results[AsyncMqttClientApi].status is Support.UNKNOWN
        switch.refuse = False
        switch.classic = True
        assert (await dev.supports(AsyncMqttClientApi)).status is Support.YES


@pytest.mark.anyio
async def test_async_cached_no_is_not_downgraded() -> None:
    switch = Switch({"something-else": {"v1": {}}})
    async with async_device(switch) as dev:
        assert (await dev.supports(AsyncOauthCcgrantApi)).status is Support.NO
        switch.refuse = True
        assert (await dev.supports_many([AsyncOauthCcgrantApi]))[AsyncOauthCcgrantApi].status is Support.NO


@pytest.mark.anyio
async def test_async_no_evidence_is_unknown_and_uncached() -> None:
    switch = Switch({"oauth-ccgrant": {"v1": {}}})
    switch.refuse = True
    async with async_device(switch) as dev:
        assert (await dev.supports(AsyncOauthCcgrantApi)).status is Support.UNKNOWN
        switch.refuse = False
        assert (await dev.supports(AsyncOauthCcgrantApi)).status is Support.YES

