# GENERATED from specs/apis/network-video/ptz-driver-management.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""List the PTZ drivers and activate or deactivate an external PTZ device driver (device type, device ID) per video channel.

Docs: https://developer.axis.com/vapix/network-video/pantiltzoom-api/
"""

from __future__ import annotations

from typing import Annotated

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Text, Xml
from .._protocols.xmlmap import XmlField, XmlMap
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

DriverState = Annotated[int, Field(ge=0, le=2)]


class DeviceIdRange(Model):
    minimum: int | None = None
    """The lowest device ID the driver accepts."""
    maximum: int | None = None
    """The highest device ID the driver accepts."""


class DriverEntry(Model):
    id: int
    """The driver ID."""
    driver: str | None = None
    """The driver name."""
    driver_version: str | None = Field(
        default=None, validation_alias="driverVersion", serialization_alias="driverVersion"
    )
    """The driver version."""
    installed: list[int] | None = None
    """The video channels where the driver is active. Empty when it is active on none."""
    device_types: list[str] | None = Field(
        default=None, validation_alias="deviceTypes", serialization_alias="deviceTypes"
    )
    """The device types the driver supports. Only present when the driver supports selecting a device type."""
    device_id_range: DeviceIdRange | None = Field(
        default=None, validation_alias="deviceIdRange", serialization_alias="deviceIdRange"
    )
    """The range of device IDs that can be assigned to a device managed by the driver."""


class ActiveDriver(Model):
    status: DriverState | None = None
    driver_id: int | None = Field(default=None, validation_alias="driverId", serialization_alias="driverId")
    """The ID of the active driver."""
    device_type: str | None = Field(default=None, validation_alias="deviceType", serialization_alias="deviceType")
    """The device type of the active driver."""
    device_id: int | None = Field(default=None, validation_alias="deviceId", serialization_alias="deviceId")
    """The device ID of the active driver."""


class ChannelStatus(Model):
    channel: int
    """The video channel number."""
    active_driver: ActiveDriver | None = Field(
        default=None, validation_alias="activeDriver", serialization_alias="activeDriver"
    )
    """The driver active on the channel. Absent when the channel has no driver."""


class DriverStatus(Model):
    channels: list[ChannelStatus] | None = None


class DriverList(Model):
    drivers: list[DriverEntry] | None = None
    status: DriverStatus | None = None
    """The driver status of every channel. Present when ``status`` was requested."""


class ListDriversRequest(Model):
    status: bool | None = None
    """Append the driver status of all channels to the reply. Default: False."""


class ActivateDriverRequest(Model):
    driverid: int | None = Field(default=None, ge=0)
    """The driver ID from ``list_drivers``. 0 deactivates the active driver without installing another. Default: 0."""
    channel: int | None = Field(default=None, ge=1)
    """The video channel where the driver is installed. Default: 1."""
    device_type: str | None = Field(default=None, validation_alias="deviceType", serialization_alias="deviceType")
    """The device type for drivers that support hardware variants (see ``DriverEntry.device_types``). Defaults to the first listed device type, without a guarantee that communication succeeds."""
    device_id: int | None = Field(default=None, validation_alias="deviceId", serialization_alias="deviceId")
    """The address of the device when several are daisy chained (see ``DriverEntry.device_id_range``). Defaults to the channel number."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/ptz/ptzuploader.cgi"

INFO = ApiInfo(
    id="ptz-driver-management",
    name="PTZ driver management API",
    family=Family.CGI,
    discovery=(
        ApiDiscovery("ptz-driver-management"),
        ParamDiscovery("Properties.PTZ.DriverManagement", "yes"),
        ParamDiscovery("Properties.PTZ.EmbeddedDrivers", "yes"),
    ),
    docs=("https://developer.axis.com/vapix/network-video/pantiltzoom-api/",),
)


class OPS:
    list_drivers = Operation(
        INFO,
        "list_drivers",
        CgiBinding(
            PATH,
            fixed_query=(("list", "yes"),),
            args=(CgiArg("status", style="axis_bool"),),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "drivers",
                            source="path",
                            name="driverentry",
                            many=True,
                            nested=XmlMap(
                                fields=(
                                    XmlField("id", source="child"),
                                    XmlField("driver", source="child"),
                                    XmlField("driverVersion", source="child", name="driverversion"),
                                    XmlField("installed", source="path", name="installed/ch", many=True),
                                    XmlField("deviceTypes", source="path", name="deviceTypes/deviceType", many=True),
                                    XmlField(
                                        "deviceIdRange",
                                        source="path",
                                        nested=XmlMap(
                                            fields=(
                                                XmlField("minimum", source="child", name="min"),
                                                XmlField("maximum", source="child", name="max"),
                                            )
                                        ),
                                    ),
                                )
                            ),
                        ),
                        XmlField(
                            "status",
                            source="path",
                            nested=XmlMap(
                                fields=(
                                    XmlField(
                                        "channels",
                                        source="path",
                                        name="channel",
                                        many=True,
                                        nested=XmlMap(
                                            fields=(
                                                XmlField("channel", name="id"),
                                                XmlField(
                                                    "activeDriver",
                                                    source="path",
                                                    nested=XmlMap(
                                                        fields=(
                                                            XmlField("status", source="child", name="driverStatus"),
                                                            XmlField("driverId", source="child"),
                                                            XmlField(
                                                                "deviceType", source="child", name="driverDeviceType"
                                                            ),
                                                            XmlField("deviceId", source="child", name="driverDeviceId"),
                                                        )
                                                    ),
                                                ),
                                            )
                                        ),
                                    ),
                                )
                            ),
                        ),
                    )
                )
            ),
        ),
        params=ListDriversRequest,
        result=DriverList,
        access="admin",
        effect="read",
        errors={
            400: ErrorCode("The listing failed.", "invalid_argument"),
            409: ErrorCode("The product is not configured to use uploadable PTZ driver mode.", "unsupported"),
        },
    )
    get_driver_status = Operation(
        INFO,
        "get_driver_status",
        CgiBinding(
            PATH,
            fixed_query=(("status", "yes"),),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "channels",
                            source="path",
                            name="channel",
                            many=True,
                            nested=XmlMap(
                                fields=(
                                    XmlField("channel", name="id"),
                                    XmlField(
                                        "activeDriver",
                                        source="path",
                                        nested=XmlMap(
                                            fields=(
                                                XmlField("status", source="child", name="driverStatus"),
                                                XmlField("driverId", source="child"),
                                                XmlField("deviceType", source="child", name="driverDeviceType"),
                                                XmlField("deviceId", source="child", name="driverDeviceId"),
                                            )
                                        ),
                                    ),
                                )
                            ),
                        ),
                    ),
                    root="status",
                )
            ),
        ),
        result=DriverStatus,
        access="admin",
        effect="read",
        errors={
            400: ErrorCode("The status request failed.", "invalid_argument"),
            409: ErrorCode("The product is not configured to use uploadable PTZ driver mode.", "unsupported"),
        },
    )
    activate_driver = Operation(
        INFO,
        "activate_driver",
        CgiBinding(
            "/axis-cgi/ptz/ptzupgrader.cgi",
            args=(
                CgiArg("driverid"),
                CgiArg("channel"),
                CgiArg("device_type", wire="deviceType"),
                CgiArg("device_id", wire="deviceId"),
            ),
            reply=Text(),
        ),
        params=ActivateDriverRequest,
        access="admin",
        effect="action",
        errors={
            400: ErrorCode("Invalid request.", "invalid_argument"),
            409: ErrorCode("The product is not configured to use uploadable PTZ driver mode.", "unsupported"),
            500: ErrorCode("Misconfiguration or hardware error.", "internal"),
            501: ErrorCode("A driver is already installed on the channel."),
        },
    )


# ---------------------------------------------------------------------------
# API classes


class PtzDriverManagementApi(SyncApi):
    """PTZ driver management API (``ptz-driver-management``)."""

    INFO = INFO

    def list_drivers(
        self, status: bool | MISSING = MISSING, *, request_options: RequestOptions | None = None
    ) -> DriverList:
        """List the available PTZ drivers, optionally with the driver status of every channel.

        Access: admin.
        """
        return self._run(OPS.list_drivers, None, {"status": status}, request_options)

    def get_driver_status(self, *, request_options: RequestOptions | None = None) -> DriverStatus:
        """Get the driver status of every video channel. Access: admin."""
        return self._run(OPS.get_driver_status, None, {}, request_options)

    def activate_driver(
        self,
        driverid: int | MISSING = MISSING,
        *,
        channel: int | MISSING = MISSING,
        device_type: str | MISSING = MISSING,
        device_id: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Activate a driver on a video channel, change its device type or device ID, or deactivate it (driverid 0).

        An external PTZ device driver active on the channel is deactivated when a new driver is activated.
        Only one external driver can be active at a time. Check the result with ``get_driver_status``.

        Access: admin.
        """
        self._run(
            OPS.activate_driver,
            None,
            {"driverid": driverid, "channel": channel, "device_type": device_type, "device_id": device_id},
            request_options,
        )


class AsyncPtzDriverManagementApi(AsyncApi):
    """PTZ driver management API (``ptz-driver-management``)."""

    INFO = INFO

    async def list_drivers(
        self, status: bool | MISSING = MISSING, *, request_options: RequestOptions | None = None
    ) -> DriverList:
        """List the available PTZ drivers, optionally with the driver status of every channel.

        Access: admin.
        """
        return await self._run(OPS.list_drivers, None, {"status": status}, request_options)

    async def get_driver_status(self, *, request_options: RequestOptions | None = None) -> DriverStatus:
        """Get the driver status of every video channel. Access: admin."""
        return await self._run(OPS.get_driver_status, None, {}, request_options)

    async def activate_driver(
        self,
        driverid: int | MISSING = MISSING,
        *,
        channel: int | MISSING = MISSING,
        device_type: str | MISSING = MISSING,
        device_id: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Activate a driver on a video channel, change its device type or device ID, or deactivate it (driverid 0).

        An external PTZ device driver active on the channel is deactivated when a new driver is activated.
        Only one external driver can be active at a time. Check the result with ``get_driver_status``.

        Access: admin.
        """
        await self._run(
            OPS.activate_driver,
            None,
            {"driverid": driverid, "channel": channel, "device_type": device_type, "device_id": device_id},
            request_options,
        )
