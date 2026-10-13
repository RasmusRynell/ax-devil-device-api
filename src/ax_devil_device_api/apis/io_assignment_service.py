# GENERATED from specs/apis/physical-access-control/io-assignment-service.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""The I/O assignment service is used to assign I/O:s to other services and to retrieve information about available I/O:s and the services’ I/O requirements.

Docs: https://developer.axis.com/vapix/physical-access-control/io-assignment-service/
"""

from __future__ import annotations

from typing import Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ServiceDiscovery
from .._protocols.service_json import ServiceJsonBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class PinInfo(Model):
    """A physical pin used by an I/O."""

    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """Physical pin. Naming convention connector type name:pinnbr, for example Door IN 1:1:GND, Door IN 1:2:IN, Reader Data 1:5. GND means a dedicated ground pin, IN an input, I/O either an input or an output, OUT an output."""
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    """Description of the pin."""


class IoInfo(Model):
    """Which physical pins an I/O uses and which modes it can be used for."""

    io_name: str = Field(validation_alias="IoName", serialization_alias="IoName")
    """Name of the I/O."""
    io_mode: list[str] | None = Field(default=None, validation_alias="IoMode", serialization_alias="IoMode")
    """Modes the I/O can be used with, for example `inout:pu/gnd`."""
    pin_info: list[PinInfo] | None = Field(default=None, validation_alias="PinInfo", serialization_alias="PinInfo")
    """The physical pins the I/O uses."""


class IoUser(Model):
    """Entity to assign I/Os to, a usage of a specific token."""

    type: str | None = Field(default=None, validation_alias="Type", serialization_alias="Type")
    """Which type of I/O user it is, for example `doorcontrol` or `idpoint`."""
    token: str | None = None
    """Token that identifies the specific entity."""
    usage: str | None = Field(default=None, validation_alias="Usage", serialization_alias="Usage")
    """Short name of the usage, for example `Lock_Standard`."""
    multi_io: bool | None = Field(default=None, validation_alias="MultiIo", serialization_alias="MultiIo")
    """True if multiple I/Os can be assigned to this IoUser."""


class IoUserInfo(Model):
    """What an IoUser needs an I/O for, and which modes it can use."""

    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """Informative name of the user."""
    io_mode: list[str] | None = Field(default=None, validation_alias="IoMode", serialization_alias="IoMode")
    """Modes the IoUser can use."""
    io_user: IoUser | None = Field(default=None, validation_alias="IoUser", serialization_alias="IoUser")


class IoAssignment(Model):
    """Which mode an I/O uses and which IoUsers it is assigned to. An empty `IoUser` list unassigns the I/O."""

    io_name: str | None = Field(default=None, validation_alias="IoName", serialization_alias="IoName")
    """Name of the I/O to assign."""
    io_mode: str | None = Field(default=None, validation_alias="IoMode", serialization_alias="IoMode")
    """The mode to configure the I/O to use. Must be one of the modes in the I/O's IoInfo and in every assigned IoUser's IoUserInfo."""
    io_user: list[IoUser] | None = Field(default=None, validation_alias="IoUser", serialization_alias="IoUser")
    """IoUsers to assign the I/O to."""


IoAssignmentErrorCode = Literal[
    "Other",
    "Unknown",
    "IoDoesNotExist",
    "IoUserServiceDoesNotExist",
    "IoUserTokenDoesNotExist",
    "IoUserUsageDoesNotExist",
    "MultipleIoNotAllowed",
    "ModeAlreadyAssignedInRequest",
    "ModeNotAllowedForIo",
    "ModeNotAllowedForIoUser",
    "DuplicateIoAssignment",
]


class IoAssignmentError(Model):
    """A failed assignment."""

    io_name: str | None = Field(default=None, validation_alias="IoName", serialization_alias="IoName")
    """Name of the I/O that could not be assigned."""
    io_mode: str | None = Field(default=None, validation_alias="IoMode", serialization_alias="IoMode")
    """The mode that was requested."""
    io_user: list[IoUser] | None = Field(default=None, validation_alias="IoUser", serialization_alias="IoUser")
    """The IoUsers the I/O was to be assigned to."""
    error: IoAssignmentErrorCode | None = Field(default=None, validation_alias="Error", serialization_alias="Error")
    """Why the assignment failed."""


class IoAssignmentList(Model):
    io_assignment: list[IoAssignment] | None = Field(
        default=None, validation_alias="IoAssignment", serialization_alias="IoAssignment"
    )


class IoUserInfoList(Model):
    io_user_info: list[IoUserInfo] | None = Field(
        default=None, validation_alias="IoUserInfo", serialization_alias="IoUserInfo"
    )


class IoInfoList(Model):
    io_info: list[IoInfo] | None = Field(default=None, validation_alias="IoInfo", serialization_alias="IoInfo")


class SetIoAssignmentRequest(Model):
    io_assignment: list[IoAssignment] | None = Field(
        default=None, validation_alias="IoAssignment", serialization_alias="IoAssignment"
    )


class SetIoAssignmentResult(Model):
    io_assignment_error: list[IoAssignmentError] | None = Field(
        default=None, validation_alias="IoAssignmentError", serialization_alias="IoAssignmentError"
    )
    """Failed assignments; empty if all succeeded."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/vapix/pin"

INFO = ApiInfo(
    id="io-assignment-service",
    name="I/O assignment service",
    family=Family.SERVICE_JSON,
    discovery=(ServiceDiscovery("http://www.axis.com/vapix/ws/AxisIo"),),
    docs=(
        "https://developer.axis.com/vapix/physical-access-control/io-assignment-service/",
        "https://developer.axis.com/vapix/physical-access-control/",
        "https://developer.axis.com/vapix/physical-access-control/peripherals/",
    ),
)


class OPS:
    get_io_assignment_list = Operation(
        INFO,
        "get_io_assignment_list",
        ServiceJsonBinding(PATH, "axisio:GetIoAssignmentList"),
        result=IoAssignmentList,
        access="admin",
        effect="read",
    )
    get_io_user_info_list = Operation(
        INFO,
        "get_io_user_info_list",
        ServiceJsonBinding(PATH, "axisio:GetIoUserInfoList"),
        result=IoUserInfoList,
        access="admin",
        effect="read",
    )
    get_io_info_list = Operation(
        INFO,
        "get_io_info_list",
        ServiceJsonBinding(PATH, "axisio:GetIoInfoList"),
        result=IoInfoList,
        access="admin",
        effect="read",
    )
    set_io_assignment = Operation(
        INFO,
        "set_io_assignment",
        ServiceJsonBinding(PATH, "axisio:SetIoAssignment"),
        params=SetIoAssignmentRequest,
        result=SetIoAssignmentResult,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class IoAssignmentServiceApi(SyncApi):
    """I/O assignment service (``io-assignment-service``)."""

    INFO = INFO

    def get_io_assignment_list(self, *, request_options: RequestOptions | None = None) -> IoAssignmentList:
        """Get all I/O assignments. Access: admin."""
        return self._run(OPS.get_io_assignment_list, None, {}, request_options)

    def get_io_user_info_list(self, *, request_options: RequestOptions | None = None) -> IoUserInfoList:
        """Get what every IoUser (door, IdPoint and so on) needs an I/O for. Access: admin."""
        return self._run(OPS.get_io_user_info_list, None, {}, request_options)

    def get_io_info_list(self, *, request_options: RequestOptions | None = None) -> IoInfoList:
        """Get all I/Os the door controller offers, with the physical pins each uses. Access: admin."""
        return self._run(OPS.get_io_info_list, None, {}, request_options)

    @overload
    def set_io_assignment(
        self, request: SetIoAssignmentRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetIoAssignmentResult: ...
    @overload
    def set_io_assignment(
        self, /, *, io_assignment: list[IoAssignment] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> SetIoAssignmentResult: ...
    def set_io_assignment(
        self,
        request: SetIoAssignmentRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetIoAssignmentResult:
        """Assign I/Os to IoUsers, or unassign them with an empty IoUser list.

        Assigning an I/O unassigns every other I/O that uses any of the same physical pins. The result lists
        the assignments that failed; it is empty when all succeeded. The call does not replace the
        assignments that are not mentioned in the request.

        Changes only the entries given; entries that do not exist yet may be created. Access: admin.
        """
        return self._run(OPS.set_io_assignment, request, kwargs, request_options)


class AsyncIoAssignmentServiceApi(AsyncApi):
    """I/O assignment service (``io-assignment-service``)."""

    INFO = INFO

    async def get_io_assignment_list(self, *, request_options: RequestOptions | None = None) -> IoAssignmentList:
        """Get all I/O assignments. Access: admin."""
        return await self._run(OPS.get_io_assignment_list, None, {}, request_options)

    async def get_io_user_info_list(self, *, request_options: RequestOptions | None = None) -> IoUserInfoList:
        """Get what every IoUser (door, IdPoint and so on) needs an I/O for. Access: admin."""
        return await self._run(OPS.get_io_user_info_list, None, {}, request_options)

    async def get_io_info_list(self, *, request_options: RequestOptions | None = None) -> IoInfoList:
        """Get all I/Os the door controller offers, with the physical pins each uses. Access: admin."""
        return await self._run(OPS.get_io_info_list, None, {}, request_options)

    @overload
    async def set_io_assignment(
        self, request: SetIoAssignmentRequest, /, *, request_options: RequestOptions | None = None
    ) -> SetIoAssignmentResult: ...
    @overload
    async def set_io_assignment(
        self, /, *, io_assignment: list[IoAssignment] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> SetIoAssignmentResult: ...
    async def set_io_assignment(
        self,
        request: SetIoAssignmentRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> SetIoAssignmentResult:
        """Assign I/Os to IoUsers, or unassign them with an empty IoUser list.

        Assigning an I/O unassigns every other I/O that uses any of the same physical pins. The result lists
        the assignments that failed; it is empty when all succeeded. The call does not replace the
        assignments that are not mentioned in the request.

        Changes only the entries given; entries that do not exist yet may be created. Access: admin.
        """
        return await self._run(OPS.set_io_assignment, request, kwargs, request_options)
