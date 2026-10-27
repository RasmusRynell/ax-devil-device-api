# GENERATED from specs/apis/device-configuration/basic-device-info-v2-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""The VAPIX® Basic device info API makes it possible to turn on/off anonymous access to a set of Basic Device Info properties on the device.

Docs: https://developer.axis.com/vapix/device-configuration/basic-device-info-api/
"""

from __future__ import annotations

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class BasicDeviceInfo(Model):
    """The whole API tree."""

    allow_anonymous: bool | None = Field(
        default=None, validation_alias="allowAnonymous", serialization_alias="allowAnonymous"
    )
    """Allow anonymous users to access the get properties functions"""


class SetAllowAnonymousRequest(Model):
    allow_anonymous: bool = Field(validation_alias="allowAnonymous", serialization_alias="allowAnonymous")
    """Allow anonymous users to access the get properties functions"""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/basic-device-info/v2"

INFO = ApiInfo(
    id="basic-device-info-v2-config",
    name="Basic device info",
    family=Family.DCA,
    discovery=(DcaDiscovery("basic-device-info", "v2"),),
    docs=("https://developer.axis.com/vapix/device-configuration/basic-device-info-api/",),
)


class OPS:
    get_all = Operation(INFO, "get_all", DcaBinding("GET", ROOT), result=BasicDeviceInfo, access="admin", effect="read")
    get_allow_anonymous = Operation(
        INFO,
        "get_allow_anonymous",
        DcaBinding("GET", f"{ROOT}/allowAnonymous"),
        result=bool,
        access="viewer",
        effect="read",
    )
    set_allow_anonymous = Operation(
        INFO,
        "set_allow_anonymous",
        DcaBinding("PATCH", f"{ROOT}/allowAnonymous", body="value", body_field="allowAnonymous"),
        params=SetAllowAnonymousRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class BasicDeviceInfoConfigApi(SyncApi):
    """Basic device info (``basic-device-info-v2-config``, v2)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> BasicDeviceInfo:
        """All data of the Basic device info API. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    def get_allow_anonymous(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether anonymous access to the basic device info properties is allowed. Access: viewer."""
        return self._run(OPS.get_allow_anonymous, None, {}, request_options)

    def set_allow_anonymous(self, *, allow_anonymous: bool, request_options: RequestOptions | None = None) -> None:
        """Allow or deny anonymous access to the basic device info properties.

        Anonymous access goes through ``/axis-cgi/basicdeviceinfo.cgi``.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_allow_anonymous, None, {"allow_anonymous": allow_anonymous}, request_options)


class AsyncBasicDeviceInfoConfigApi(AsyncApi):
    """Basic device info (``basic-device-info-v2-config``, v2)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> BasicDeviceInfo:
        """All data of the Basic device info API. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def get_allow_anonymous(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether anonymous access to the basic device info properties is allowed. Access: viewer."""
        return await self._run(OPS.get_allow_anonymous, None, {}, request_options)

    async def set_allow_anonymous(
        self, *, allow_anonymous: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Allow or deny anonymous access to the basic device info properties.

        Anonymous access goes through ``/axis-cgi/basicdeviceinfo.cgi``.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_allow_anonymous, None, {"allow_anonymous": allow_anonymous}, request_options)
