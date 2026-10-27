"""Beta DCA APIs are listed by /config/discover under their major version ("v1" with "state": "beta").

Only the REST root carries the suffix (``/config/rest/<id>/v1beta``). Source: docs "Device Configuration APIs", section
Discovery (``rest_api: /config/rest/ssh/v1beta`` under ``ssh -> v1`` with ``state: beta``).
"""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest
import yaml

from ax_devil_device_api import Device, Support
from ax_devil_device_api.apis.audio_multicast_ctrl import AudioMulticastCtrlApi
from ax_devil_device_api.apis.cellular_routing import CellularRoutingApi
from ax_devil_device_api.apis.unified_proxy_configuration import UnifiedProxyConfigurationApi

BETA_APIS = {
    "audio-multicast-ctrl": AudioMulticastCtrlApi,
    "cellular-routing": CellularRoutingApi,
    "unified-proxy-configuration": UnifiedProxyConfigurationApi,
}


def discover(apis: dict[str, object]) -> Device:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/config/discover":
            return httpx.Response(200, json={"framework_version": "1.0.0", "apis": apis})
        return httpx.Response(404, text="not found")

    return Device("cam", credentials=("u", "p"), transport=httpx.MockTransport(handler))


def beta_entry(api: str) -> dict[str, object]:
    return {"v1": {"state": "beta", "version": "1.0.0-beta.1", "rest_api": f"/config/rest/{api}/v1beta"}}


@pytest.mark.parametrize("api", sorted(BETA_APIS))
def test_a_conforming_beta_listing_is_found(api: str) -> None:
    with discover({api: beta_entry(api)}) as dev:
        result = dev.supports(BETA_APIS[api])
    assert result.status is Support.YES, result


@pytest.mark.parametrize("api", sorted(BETA_APIS))
def test_the_rest_suffix_is_not_a_discovery_key(api: str) -> None:
    with discover({api: {"v1beta": {"state": "beta"}}}) as dev:
        assert dev.supports(BETA_APIS[api]).status is Support.NO


def test_no_spec_looks_for_a_suffixed_version_in_discovery() -> None:
    root = Path(__file__).resolve().parents[2] / "specs" / "apis"
    offenders = []
    for path in sorted(root.rglob("*.yaml")):
        for entry in yaml.safe_load(path.read_text()).get("discovery") or []:
            version = entry.get("dca", {}).get("version", "")
            if version.endswith(("beta", "alpha")):
                offenders.append(f"{path.name}: {version}")
    assert offenders == []
