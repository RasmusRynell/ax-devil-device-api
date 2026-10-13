# GENERATED from specs/apis/device-configuration/object-snapshot-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure cropped object snapshots attached to analytics metadata.

Docs: https://developer.axis.com/vapix/device-configuration/object-snapshot-configuration/
"""

from __future__ import annotations

from pydantic import MISSING

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

Enabled = bool
Margin = bool


class ObjectSnapshot(Model):
    """The whole API tree."""

    enabled: Enabled | None = None
    margin: Margin | None = None


class UpdateAllRequest(Model):
    """Arguments of ``update_all``. Only the given fields change."""

    enabled: Enabled | None = None
    margin: Margin | None = None

    @classmethod
    def from_current(cls, snapshot: ObjectSnapshot) -> UpdateAllRequest:
        """A request that rewrites ``snapshot`` unchanged: copy it, edit fields, send it back."""
        data = snapshot.request_data()
        return cls.from_response_data(data)


class SetEnabledRequest(Model):
    enabled: Enabled


class SetMarginRequest(Model):
    margin: Margin


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/object-snapshot/v1"

INFO = ApiInfo(
    id="object-snapshot-config",
    name="Object snapshot",
    family=Family.DCA,
    discovery=(DcaDiscovery("object-snapshot", "v1"),),
    docs=("https://developer.axis.com/vapix/device-configuration/object-snapshot-configuration/",),
)


class OPS:
    get_all = Operation(INFO, "get_all", DcaBinding("GET", ROOT), result=ObjectSnapshot, access="admin", effect="read")
    update_all = Operation(
        INFO,
        "update_all",
        DcaBinding("PATCH", ROOT, body="object"),
        params=UpdateAllRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_enabled = Operation(
        INFO, "get_enabled", DcaBinding("GET", f"{ROOT}/enabled"), result=Enabled, access="admin", effect="read"
    )
    set_enabled = Operation(
        INFO,
        "set_enabled",
        DcaBinding("PATCH", f"{ROOT}/enabled", body="value", body_field="enabled"),
        params=SetEnabledRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_margin = Operation(
        INFO, "get_margin", DcaBinding("GET", f"{ROOT}/margin"), result=Margin, access="admin", effect="read"
    )
    set_margin = Operation(
        INFO,
        "set_margin",
        DcaBinding("PATCH", f"{ROOT}/margin", body="value", body_field="margin"),
        params=SetMarginRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class ObjectSnapshotApi(SyncApi):
    """Object snapshot (``object-snapshot-config``, v1)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> ObjectSnapshot:
        """All Object Snapshot settings. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    def update_all(
        self,
        *,
        enabled: Enabled | MISSING = MISSING,
        margin: Margin | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update the Object Snapshot settings. Changes only the fields given. Access: admin."""
        self._run(OPS.update_all, None, {"enabled": enabled, "margin": margin}, request_options)

    def get_enabled(self, *, request_options: RequestOptions | None = None) -> Enabled:
        """Whether Object Snapshot is enabled. Access: admin."""
        return self._run(OPS.get_enabled, None, {}, request_options)

    def set_enabled(self, *, enabled: Enabled, request_options: RequestOptions | None = None) -> None:
        """Enable or disable Object Snapshot. Changes only the fields given. Access: admin."""
        self._run(OPS.set_enabled, None, {"enabled": enabled}, request_options)

    def get_margin(self, *, request_options: RequestOptions | None = None) -> Margin:
        """Whether snapshots include a margin around the object. Access: admin."""
        return self._run(OPS.get_margin, None, {}, request_options)

    def set_margin(self, *, margin: Margin, request_options: RequestOptions | None = None) -> None:
        """Include or exclude a margin around the object in snapshots.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_margin, None, {"margin": margin}, request_options)


class AsyncObjectSnapshotApi(AsyncApi):
    """Object snapshot (``object-snapshot-config``, v1)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> ObjectSnapshot:
        """All Object Snapshot settings. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def update_all(
        self,
        *,
        enabled: Enabled | MISSING = MISSING,
        margin: Margin | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update the Object Snapshot settings. Changes only the fields given. Access: admin."""
        await self._run(OPS.update_all, None, {"enabled": enabled, "margin": margin}, request_options)

    async def get_enabled(self, *, request_options: RequestOptions | None = None) -> Enabled:
        """Whether Object Snapshot is enabled. Access: admin."""
        return await self._run(OPS.get_enabled, None, {}, request_options)

    async def set_enabled(self, *, enabled: Enabled, request_options: RequestOptions | None = None) -> None:
        """Enable or disable Object Snapshot. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_enabled, None, {"enabled": enabled}, request_options)

    async def get_margin(self, *, request_options: RequestOptions | None = None) -> Margin:
        """Whether snapshots include a margin around the object. Access: admin."""
        return await self._run(OPS.get_margin, None, {}, request_options)

    async def set_margin(self, *, margin: Margin, request_options: RequestOptions | None = None) -> None:
        """Include or exclude a margin around the object in snapshots.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_margin, None, {"margin": margin}, request_options)
