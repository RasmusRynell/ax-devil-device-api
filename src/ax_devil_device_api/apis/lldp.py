# GENERATED from specs/apis/device-configuration/lldp-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Activate and deactivate LLDP (Link Layer Discovery Protocol) and read neighbor information.

Docs: https://developer.axis.com/vapix/device-configuration/lldp-configuration-api/
"""

from __future__ import annotations

from typing import Annotated, ClassVar, Literal

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

ChassisIDSubType = Literal[
    "ChassisComponent",
    "InterfaceAlias",
    "PortComponent",
    "MACAddress",
    "NetworkAddress",
    "InterfaceName",
    "LocallyAssigned",
]


class ChassisID(Model):
    """The chassis ID type"""

    sub_type: ChassisIDSubType = Field(validation_alias="subType", serialization_alias="subType")
    """Chassis ID subtype"""
    value: str
    """A chassis ID of the type specified by the subType field"""


MgmtIPSubType = Literal["IPv4", "IPv6"]


class MgmtIP(Model):
    """The management IP type"""

    sub_type: MgmtIPSubType = Field(validation_alias="subType", serialization_alias="subType")
    """Management IP address subtype"""
    value: str
    """A management IP address of the type specified by the subType field"""


PositiveInt = Annotated[int, Field(ge=0)]
PortIDSubType = Literal[
    "InterfaceAlias",
    "PortComponent",
    "MACAddress",
    "NetworkAddress",
    "InterfaceName",
    "AgentCircuitID",
    "LocallyAssigned",
]


class PortID(Model):
    """The port ID type"""

    sub_type: PortIDSubType = Field(validation_alias="subType", serialization_alias="subType")
    """Port ID subtype"""
    value: str
    """A port ID of the type specified by the subType field"""


Protocol = Literal["LLDP", "CDPv1", "CDPv2"]


class Neighbor(Model):
    """Neighbor information"""

    __nullable__: ClassVar[frozenset[str]] = frozenset({"mgmt_ip", "port_descr", "sys_descr", "sys_name"})
    ttl: PositiveInt = Field(validation_alias="TTL", serialization_alias="TTL")
    """Time To Live"""
    age: PositiveInt
    """Age of the neighbor information in seconds from epoch"""
    chassis_id: ChassisID = Field(validation_alias="chassisID", serialization_alias="chassisID")
    """The chassis ID of the neighbor"""
    if_name: str = Field(validation_alias="ifName", serialization_alias="ifName")
    """Name of the interface from which the information is received"""
    mgmt_ip: MgmtIP | None = Field(default=None, validation_alias="mgmtIP", serialization_alias="mgmtIP")
    """Management IP of the neighbor"""
    port_descr: str | None = Field(default=None, validation_alias="portDescr", serialization_alias="portDescr")
    """Port description of the neighbor"""
    port_id: PortID = Field(validation_alias="portID", serialization_alias="portID")
    """Port ID of the neighbor"""
    protocol: Protocol
    """The protocol used"""
    sys_descr: str | None = Field(default=None, validation_alias="sysDescr", serialization_alias="sysDescr")
    """System description of the neighbor"""
    sys_name: str | None = Field(default=None, validation_alias="sysName", serialization_alias="sysName")
    """System hostname of the neighbor"""


class Lldp(Model):
    """The whole API tree."""

    activated: bool | None = None
    """LLDP state"""
    neighbors: list[Neighbor] | None = None
    """Information about neighbors on the interface"""


class SetActivatedRequest(Model):
    activated: bool
    """LLDP state"""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/lldp/v1"

INFO = ApiInfo(
    id="lldp-config",
    name="LLDP Configuration API",
    family=Family.DCA,
    discovery=(DcaDiscovery("lldp", "v1"),),
    docs=("https://developer.axis.com/vapix/device-configuration/lldp-configuration-api/",),
)


class OPS:
    get_all = Operation(INFO, "get_all", DcaBinding("GET", ROOT), result=Lldp, access="admin", effect="read")
    get_activated = Operation(
        INFO, "get_activated", DcaBinding("GET", f"{ROOT}/activated"), result=bool, access="admin", effect="read"
    )
    list_neighbors = Operation(
        INFO,
        "list_neighbors",
        DcaBinding("GET", f"{ROOT}/neighbors"),
        result=list[Neighbor],
        access="admin",
        effect="read",
    )
    set_activated = Operation(
        INFO,
        "set_activated",
        DcaBinding("PATCH", f"{ROOT}/activated", body="value", body_field="activated"),
        params=SetActivatedRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class LldpApi(SyncApi):
    """LLDP Configuration API (``lldp-config``, v1)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> Lldp:
        """All data of the LLDP Configuration API. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    def get_activated(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether LLDP is activated. Access: admin."""
        return self._run(OPS.get_activated, None, {}, request_options)

    def list_neighbors(self, *, request_options: RequestOptions | None = None) -> list[Neighbor]:
        """Neighbor information from all LLDP configured interfaces. Access: admin."""
        return self._run(OPS.list_neighbors, None, {}, request_options)

    def set_activated(self, activated: bool, *, request_options: RequestOptions | None = None) -> None:
        """Activate or deactivate LLDP. Deactivating LLDP also deactivates fabric attach network automation and may affect PoE power negotiation.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_activated, None, {"activated": activated}, request_options)


class AsyncLldpApi(AsyncApi):
    """LLDP Configuration API (``lldp-config``, v1)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> Lldp:
        """All data of the LLDP Configuration API. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def get_activated(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether LLDP is activated. Access: admin."""
        return await self._run(OPS.get_activated, None, {}, request_options)

    async def list_neighbors(self, *, request_options: RequestOptions | None = None) -> list[Neighbor]:
        """Neighbor information from all LLDP configured interfaces. Access: admin."""
        return await self._run(OPS.list_neighbors, None, {}, request_options)

    async def set_activated(self, activated: bool, *, request_options: RequestOptions | None = None) -> None:
        """Activate or deactivate LLDP. Deactivating LLDP also deactivates fabric attach network automation and may affect PoE power negotiation.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_activated, None, {"activated": activated}, request_options)
