"""Device summary and API support overview, built on ``identity()``, ``capabilities()`` and ``supports()``."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

from .._runtime.capabilities import Capabilities, DeviceIdentity, Support, SupportResult
from ..device import AsyncDevice, Device
from .registry import ApiEntry, load_all


@dataclass(frozen=True)
class DeviceSummary:
    """What a device says about itself, for a quick look or a health report."""

    host: str
    model: str | None
    product_number: str | None
    full_name: str | None
    serial_number: str | None
    firmware_version: str | None
    hardware_id: str | None
    architecture: str | None
    classic_apis: Mapping[str, str] | None
    """Classic API id -> version; ``None`` if that discovery probe failed."""
    dca_apis: Mapping[str, tuple[str, ...]] | None
    """Device Configuration API -> path versions; ``None`` if that probe failed."""
    applications: Mapping[str, str] | None
    probe_errors: Mapping[str, str] = field(default_factory=dict)
    observed_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["observed_at"] = self.observed_at.isoformat() if self.observed_at else None
        return data


def _summary(host: str, identity: DeviceIdentity, caps: Capabilities) -> DeviceSummary:
    return DeviceSummary(
        host=host,
        model=identity.model,
        product_number=identity.product_number,
        full_name=identity.full_name,
        serial_number=identity.serial_number,
        firmware_version=identity.firmware_version,
        hardware_id=identity.hardware_id,
        architecture=identity.architecture,
        classic_apis=dict(caps.classic_apis) if caps.classic_apis is not None else None,
        dca_apis={k: tuple(sorted(v)) for k, v in caps.dca_apis.items()} if caps.dca_apis is not None else None,
        applications=dict(caps.applications) if caps.applications is not None else None,
        probe_errors=dict(caps.errors),
        observed_at=caps.observed_at,
    )


def device_summary(dev: Device) -> DeviceSummary:
    """Identity plus discovery results. Failed discovery probes are reported in ``probe_errors``; identity errors raise."""
    identity = dev.identity()
    return _summary(dev.config.host, identity, dev.capabilities())


async def async_device_summary(dev: AsyncDevice) -> DeviceSummary:
    identity = await dev.identity()
    return _summary(dev.config.host, identity, await dev.capabilities())


def api_support(dev: Device, entries: list[ApiEntry] | None = None) -> dict[str, SupportResult]:
    """``SupportResult`` for every generated API (``dev.apis.<name>`` -> result). Uses one capability snapshot: a failing probe is run once, not once per API."""
    entries = entries if entries is not None else load_all()
    results = dev.supports_many([e.sync_class for e in entries])
    return {e.name: results[e.sync_class] for e in entries}


async def async_api_support(dev: AsyncDevice, entries: list[ApiEntry] | None = None) -> dict[str, SupportResult]:
    entries = entries if entries is not None else load_all()
    results = await dev.supports_many([e.async_class for e in entries])
    return {e.name: results[e.async_class] for e in entries}


def supported_apis(dev: Device) -> list[str]:
    """Names of generated APIs the device positively offers (``Support.YES``), sorted."""
    return sorted(n for n, r in api_support(dev).items() if r.status is Support.YES)


async def async_supported_apis(dev: AsyncDevice) -> list[str]:
    return sorted(n for n, r in (await async_api_support(dev)).items() if r.status is Support.YES)
