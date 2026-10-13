# GENERATED from specs/apis/device-configuration/param-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Read, export, and import /axis-cgi/param.cgi parameters through the Device Configuration API framework.

Docs: https://developer.axis.com/vapix/device-configuration/param-api/
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

ParamValue = str
ParamTree = dict[str, Any]


class ParamObjectPathRequest(Model):
    object_path: str = Field(validation_alias="objectPath", serialization_alias="objectPath")


class ImportRequest(Model):
    data: ParamTree


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/param/v2beta"

INFO = ApiInfo(
    id="param-config",
    name="Param API",
    family=Family.DCA,
    discovery=(DcaDiscovery("param", "v2"),),
    docs=("https://developer.axis.com/vapix/device-configuration/param-api/",),
)


class OPS:
    get_all = Operation(INFO, "get_all", DcaBinding("GET", ROOT), result=ParamTree, access="admin", effect="read")
    get_object = Operation(
        INFO,
        "get_object",
        DcaBinding("GET", f"{ROOT}/{{objectPath}}", key_styles=(("objectPath", "path"),)),
        params=ParamObjectPathRequest,
        result=ParamValue | ParamTree,
        access="admin",
        effect="read",
    )
    export_all = Operation(
        INFO, "export_all", DcaBinding("GET", f"{ROOT}/$export"), result=ParamTree, access="admin", effect="read"
    )
    import_all = Operation(
        INFO,
        "import_all",
        DcaBinding("PATCH", f"{ROOT}/$import", body="value", body_field="data"),
        params=ImportRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class ParamApi(SyncApi):
    """Param API (``param-config``, v2)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> ParamTree:
        """All readable param.cgi parameters, as a nested tree. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    def get_object(self, object_path: str, *, request_options: RequestOptions | None = None) -> ParamValue | ParamTree:
        """One parameter (a string) or a group (a tree), addressed by its path below the root.

        ``object_path`` is the group and parameter names joined by ``/``, for example
        ``Audio/MaxListeners``.

        Access: admin.
        """
        return self._run(OPS.get_object, None, {"object_path": object_path}, request_options)

    def export_all(self, *, request_options: RequestOptions | None = None) -> ParamTree:
        """Export all writable parameters (the ones that can be imported). Access: admin."""
        return self._run(OPS.export_all, None, {}, request_options)

    def import_all(self, data: ParamTree, *, request_options: RequestOptions | None = None) -> None:
        """Import parameters; only the given ones are updated and dynamic group instances are created as needed.

        Pass the same tree shape that ``export_all`` returns. The import type has no effect on this API.
        Parameters that fail are reported in a warning section of the response.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.import_all, None, {"data": data}, request_options)


class AsyncParamApi(AsyncApi):
    """Param API (``param-config``, v2)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> ParamTree:
        """All readable param.cgi parameters, as a nested tree. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def get_object(
        self, object_path: str, *, request_options: RequestOptions | None = None
    ) -> ParamValue | ParamTree:
        """One parameter (a string) or a group (a tree), addressed by its path below the root.

        ``object_path`` is the group and parameter names joined by ``/``, for example
        ``Audio/MaxListeners``.

        Access: admin.
        """
        return await self._run(OPS.get_object, None, {"object_path": object_path}, request_options)

    async def export_all(self, *, request_options: RequestOptions | None = None) -> ParamTree:
        """Export all writable parameters (the ones that can be imported). Access: admin."""
        return await self._run(OPS.export_all, None, {}, request_options)

    async def import_all(self, data: ParamTree, *, request_options: RequestOptions | None = None) -> None:
        """Import parameters; only the given ones are updated and dynamic group instances are created as needed.

        Pass the same tree shape that ``export_all`` returns. The import type has no effect on this API.
        Parameters that fail are reported in a warning section of the response.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.import_all, None, {"data": data}, request_options)
