# GENERATED from specs/apis/device-configuration/dnsupdate-configuration-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure the DNS name registration (DNSUpdate) of the device.

Docs: https://developer.axis.com/vapix/device-configuration/dnsupdate-configuration-api/
"""

from __future__ import annotations

from typing import Annotated

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

Ttl = Annotated[int, Field(ge=0, le=4294967295)]


class Settings(Model):
    """Configuration settings. Defaults on first boot are disabled, an empty name and a TTL of 30."""

    enabled: bool | None = None
    """The enabled state of DNSUpdate."""
    name: str | None = None
    """The name to be registered."""
    ttl: Ttl | None = None
    """The TTL used."""


class DnsupdateConfiguration(Model):
    """The whole API tree."""

    settings: Settings | None = None


class UpdateSettingsRequest(Model):
    """Arguments of ``update_settings``."""

    enabled: bool | None = None
    """The enabled state of DNSUpdate."""
    name: str | None = None
    """The name to be registered."""
    ttl: Ttl | None = None
    """The TTL used."""


class SetSettingsEnabledRequest(Model):
    enabled: bool
    """The enabled state of DNSUpdate."""


class SetSettingsNameRequest(Model):
    name: str
    """The name to be registered."""


class SetSettingsTtlRequest(Model):
    ttl: Ttl
    """The TTL used."""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/dnsupdate-configuration/v2"

INFO = ApiInfo(
    id="dnsupdate-configuration-config",
    name="DNSUpdate configuration",
    family=Family.DCA,
    discovery=(DcaDiscovery("dnsupdate-configuration", "v2"),),
    docs=("https://developer.axis.com/vapix/device-configuration/dnsupdate-configuration-api/",),
)


class OPS:
    get_all = Operation(
        INFO, "get_all", DcaBinding("GET", ROOT), result=DnsupdateConfiguration, access="admin", effect="read"
    )
    get_settings = Operation(
        INFO, "get_settings", DcaBinding("GET", f"{ROOT}/settings"), result=Settings, access="admin", effect="read"
    )
    update_settings = Operation(
        INFO,
        "update_settings",
        DcaBinding("PATCH", f"{ROOT}/settings", body="object"),
        params=UpdateSettingsRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_settings_enabled = Operation(
        INFO,
        "set_settings_enabled",
        DcaBinding("PATCH", f"{ROOT}/settings/enabled", body="value", body_field="enabled"),
        params=SetSettingsEnabledRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_settings_name = Operation(
        INFO,
        "set_settings_name",
        DcaBinding("PATCH", f"{ROOT}/settings/name", body="value", body_field="name"),
        params=SetSettingsNameRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_settings_ttl = Operation(
        INFO,
        "set_settings_ttl",
        DcaBinding("PATCH", f"{ROOT}/settings/ttl", body="value", body_field="ttl"),
        params=SetSettingsTtlRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class DnsupdateConfigurationApi(SyncApi):
    """DNSUpdate configuration (``dnsupdate-configuration-config``, v2)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> DnsupdateConfiguration:
        """All data of the DNSUpdate configuration API. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    def get_settings(self, *, request_options: RequestOptions | None = None) -> Settings:
        """Get the DNSUpdate settings. Access: admin."""
        return self._run(OPS.get_settings, None, {}, request_options)

    def update_settings(
        self,
        *,
        enabled: bool | MISSING = MISSING,
        name: str | MISSING = MISSING,
        ttl: Ttl | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update the DNSUpdate settings; only the given fields change.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.update_settings, None, {"enabled": enabled, "name": name, "ttl": ttl}, request_options)

    def set_settings_enabled(self, enabled: bool, *, request_options: RequestOptions | None = None) -> None:
        """Enable or disable DNS name registration. Changes only the fields given. Access: admin."""
        self._run(OPS.set_settings_enabled, None, {"enabled": enabled}, request_options)

    def set_settings_name(self, name: str, *, request_options: RequestOptions | None = None) -> None:
        """Set the name to register in DNS. Updates the DNS servers when DNSUpdate is enabled.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_settings_name, None, {"name": name}, request_options)

    def set_settings_ttl(self, ttl: Ttl, *, request_options: RequestOptions | None = None) -> None:
        """Set the Time To Live of the DNS records. Changes only the fields given. Access: admin."""
        self._run(OPS.set_settings_ttl, None, {"ttl": ttl}, request_options)


class AsyncDnsupdateConfigurationApi(AsyncApi):
    """DNSUpdate configuration (``dnsupdate-configuration-config``, v2)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> DnsupdateConfiguration:
        """All data of the DNSUpdate configuration API. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def get_settings(self, *, request_options: RequestOptions | None = None) -> Settings:
        """Get the DNSUpdate settings. Access: admin."""
        return await self._run(OPS.get_settings, None, {}, request_options)

    async def update_settings(
        self,
        *,
        enabled: bool | MISSING = MISSING,
        name: str | MISSING = MISSING,
        ttl: Ttl | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update the DNSUpdate settings; only the given fields change.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.update_settings, None, {"enabled": enabled, "name": name, "ttl": ttl}, request_options)

    async def set_settings_enabled(self, enabled: bool, *, request_options: RequestOptions | None = None) -> None:
        """Enable or disable DNS name registration. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_settings_enabled, None, {"enabled": enabled}, request_options)

    async def set_settings_name(self, name: str, *, request_options: RequestOptions | None = None) -> None:
        """Set the name to register in DNS. Updates the DNS servers when DNSUpdate is enabled.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_settings_name, None, {"name": name}, request_options)

    async def set_settings_ttl(self, ttl: Ttl, *, request_options: RequestOptions | None = None) -> None:
        """Set the Time To Live of the DNS records. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_settings_ttl, None, {"ttl": ttl}, request_options)
