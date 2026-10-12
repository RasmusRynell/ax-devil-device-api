# GENERATED from specs/apis/network-video/external-ip-device-info.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Store connection information (address, credentials, protocol, certificate validation) for external IP devices such as cameras, enable their events and configure the CA certificates.

Docs: https://developer.axis.com/vapix/network-video/external-ip-device-information/
"""

from __future__ import annotations

from typing import Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ErrorCode, Family, Model, Operation
from .._protocols.cgi import CgiArg, CgiBinding, Xml
from .._protocols.xmlmap import XmlField, XmlMap
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

Protocol = Literal["rtspt", "rtsph", "rtspsh"]
CertificateValidation = Literal["standard", "limited", "off"]


class ExternalIpDevice(Model):
    id: str = Field(validation_alias="Id", serialization_alias="Id")
    serial_number: str | None = Field(default=None, validation_alias="Serialnumber", serialization_alias="Serialnumber")
    description: str | None = Field(default=None, validation_alias="Description", serialization_alias="Description")
    address: str | None = Field(default=None, validation_alias="Address", serialization_alias="Address")
    username: str | None = Field(default=None, validation_alias="Username", serialization_alias="Username")
    protocol: Protocol | None = Field(default=None, validation_alias="Protocol", serialization_alias="Protocol")
    port: int | None = Field(default=None, validation_alias="Port", serialization_alias="Port")
    certificate_validation: CertificateValidation | None = Field(
        default=None, validation_alias="CertificateValidation", serialization_alias="CertificateValidation"
    )


class ExternalIpDeviceList(Model):
    devices: list[ExternalIpDevice] | None = None


class EventsEnabledState(Model):
    id: str = Field(validation_alias="Id", serialization_alias="Id")
    events_enabled: Literal["YES", "NO"] = Field(validation_alias="EventsEnabled", serialization_alias="EventsEnabled")
    """Whether events (VMD2, VMD3, VMD4 and VMDLite) are enabled."""


class CaCertificates(Model):
    ids: list[str] | None = None
    """IDs of the configured CA certificates."""


class SchemaVersions(Model):
    versions: list[str] | None = None
    """Supported schema versions as major.minor."""


class CreateDeviceRequest(Model):
    id: str
    """The unique external IP device identifier."""
    description: str | None = None
    """The external IP device description."""
    serial_number: str | None = Field(default=None, validation_alias="serialnumber", serialization_alias="serialnumber")
    """The external IP device serial number: a MAC address or an alphanumeric string."""
    address: str | None = None
    """The external IP device address or hostname. username and password are required when an address is set."""
    username: str | None = None
    """The IP device account name. Required when address is set; the account must already exist on the external IP device."""
    password: str | None = None
    """The password of username. Required when address is set."""
    protocol: Protocol | None = None
    certificate_validation: CertificateValidation | None = Field(
        default=None, validation_alias="certvalidation", serialization_alias="certvalidation"
    )
    port: int | None = Field(default=None, ge=0, le=65535)
    """Port used to fetch the event stream. The default 0 means the standard port of the protocol: 554 for rtspt, 80 for rtsph and 443 for rtspsh."""


class UpdateDeviceRequest(Model):
    id: str
    """The unique external IP device identifier."""
    description: str | None = None
    """The external IP device description."""
    serial_number: str | None = Field(default=None, validation_alias="serialnumber", serialization_alias="serialnumber")
    """The external IP device serial number: a MAC address or an alphanumeric string."""
    address: str | None = None
    """The external IP device address or hostname. username and password are required when an address is set."""
    username: str | None = None
    """The IP device account name. Required when address is set; the account must already exist on the external IP device."""
    password: str | None = None
    """The password of username. Required when address is set."""
    protocol: Protocol | None = None
    certificate_validation: CertificateValidation | None = Field(
        default=None, validation_alias="certvalidation", serialization_alias="certvalidation"
    )
    port: int | None = Field(default=None, ge=0, le=65535)
    """Port used to fetch the event stream. The default 0 means the standard port of the protocol: 554 for rtspt, 80 for rtsph and 443 for rtspsh."""


class DeleteDeviceRequest(Model):
    id: str
    """The unique external IP device identifier."""


class SetEventsEnabledRequest(Model):
    id: str
    """The unique external IP device identifier."""
    enabled: bool
    """True enables the events found on the external IP device, False disables them."""


class GetEventsEnabledRequest(Model):
    id: str
    """The unique external IP device identifier."""


class SetCaCertificatesRequest(Model):
    cert_ids: list[str] | None = Field(default=None, validation_alias="certids", serialization_alias="certids")
    """IDs of the CA certificates. Validation succeeds if the signature matches at least one of them."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/externalipdeviceinfo/create.cgi"

INFO = ApiInfo(
    id="external-ip-device-info",
    name="External IP device information",
    family=Family.CGI,
    discovery=(ApiDiscovery("ext-ip-dev-info"),),
    docs=("https://developer.axis.com/vapix/network-video/external-ip-device-information/",),
)


class OPS:
    create_device = Operation(
        INFO,
        "create_device",
        CgiBinding(
            "/axis-cgi/externalipdeviceinfo/create.cgi",
            fixed_query=(("schemaversion", "2"),),
            args=(
                CgiArg("id"),
                CgiArg("description"),
                CgiArg("serial_number", wire="serialnumber"),
                CgiArg("address"),
                CgiArg("username"),
                CgiArg("password"),
                CgiArg("protocol"),
                CgiArg("certificate_validation", wire="certvalidation"),
                CgiArg("port"),
            ),
            reply=Xml(),
        ),
        params=CreateDeviceRequest,
        access="admin",
        effect="write",
        write="create",
        errors={
            10: ErrorCode("An error occurred at system level.", "internal"),
            30: ErrorCode("Maximum amount of devices reached.", "unavailable"),
            40: ErrorCode("Invalid or no id.", "invalid_argument"),
            60: ErrorCode("Unsupported schema version.", "unsupported"),
            70: ErrorCode("Invalid request.", "invalid_argument"),
            80: ErrorCode("Processing error.", "internal"),
            150: ErrorCode("Device already exists.", "invalid_argument"),
            170: ErrorCode("Invalid description.", "invalid_argument"),
            180: ErrorCode("Invalid serialnumber.", "invalid_argument"),
            190: ErrorCode("Invalid protocol.", "invalid_argument"),
            200: ErrorCode("Invalid port.", "invalid_argument"),
            210: ErrorCode("Invalid certificate validation.", "invalid_argument"),
        },
    )
    update_device = Operation(
        INFO,
        "update_device",
        CgiBinding(
            "/axis-cgi/externalipdeviceinfo/update.cgi",
            fixed_query=(("schemaversion", "2"),),
            args=(
                CgiArg("id"),
                CgiArg("description"),
                CgiArg("serial_number", wire="serialnumber"),
                CgiArg("address"),
                CgiArg("username"),
                CgiArg("password"),
                CgiArg("protocol"),
                CgiArg("certificate_validation", wire="certvalidation"),
                CgiArg("port"),
            ),
            reply=Xml(),
        ),
        params=UpdateDeviceRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={
            10: ErrorCode("An error occurred at system level.", "internal"),
            40: ErrorCode("Invalid or no id.", "invalid_argument"),
            60: ErrorCode("Unsupported schema version.", "unsupported"),
            80: ErrorCode("Processing error.", "internal"),
            90: ErrorCode("No device.", "not_found"),
            170: ErrorCode("Invalid description.", "invalid_argument"),
            180: ErrorCode("Invalid serialnumber.", "invalid_argument"),
            190: ErrorCode("Invalid protocol.", "invalid_argument"),
            200: ErrorCode("Invalid port.", "invalid_argument"),
            210: ErrorCode("Invalid certificate validation.", "invalid_argument"),
        },
    )
    delete_device = Operation(
        INFO,
        "delete_device",
        CgiBinding(
            "/axis-cgi/externalipdeviceinfo/delete.cgi",
            fixed_query=(("schemaversion", "2"),),
            args=(CgiArg("id"),),
            reply=Xml(),
        ),
        params=DeleteDeviceRequest,
        access="admin",
        effect="write",
        write="delete",
        errors={
            10: ErrorCode("An error occurred at system level.", "internal"),
            40: ErrorCode("Invalid or no id.", "invalid_argument"),
            60: ErrorCode("Unsupported schema version.", "unsupported"),
            80: ErrorCode("Processing error.", "internal"),
            90: ErrorCode("No device.", "not_found"),
        },
    )
    list_devices = Operation(
        INFO,
        "list_devices",
        CgiBinding(
            "/axis-cgi/externalipdeviceinfo/list.cgi",
            fixed_query=(("schemaversion", "2"),),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "devices",
                            source="path",
                            name="Device",
                            many=True,
                            nested=XmlMap(
                                fields=(
                                    XmlField("Id", source="child"),
                                    XmlField("Serialnumber", source="child"),
                                    XmlField("Description", source="child"),
                                    XmlField("Address", source="child"),
                                    XmlField("Username", source="child"),
                                    XmlField("Protocol", source="child"),
                                    XmlField("Port", source="child"),
                                    XmlField("CertificateValidation", source="child"),
                                )
                            ),
                        ),
                    ),
                    root="ListDevicesSuccess",
                )
            ),
        ),
        result=ExternalIpDeviceList,
        access="admin",
        effect="read",
        errors={
            10: ErrorCode("An error occurred at system level.", "internal"),
            60: ErrorCode("Unsupported schema version.", "unsupported"),
            80: ErrorCode("Processing error.", "internal"),
        },
    )
    set_events_enabled = Operation(
        INFO,
        "set_events_enabled",
        CgiBinding(
            "/axis-cgi/externalipdeviceinfo/seteventsenabled.cgi",
            fixed_query=(("schemaversion", "2"),),
            args=(CgiArg("id"), CgiArg("enabled", style="axis_bool")),
            reply=Xml(),
        ),
        params=SetEventsEnabledRequest,
        access="admin",
        effect="write",
        write="patch",
        errors={
            10: ErrorCode("An error occurred at system level.", "internal"),
            40: ErrorCode("Invalid or no id.", "invalid_argument"),
            60: ErrorCode("Unsupported schema version.", "unsupported"),
            70: ErrorCode("Invalid request.", "invalid_argument"),
            80: ErrorCode("Processing error.", "internal"),
            90: ErrorCode("No device.", "not_found"),
        },
    )
    get_events_enabled = Operation(
        INFO,
        "get_events_enabled",
        CgiBinding(
            "/axis-cgi/externalipdeviceinfo/geteventsenabled.cgi",
            fixed_query=(("schemaversion", "2"),),
            args=(CgiArg("id"),),
            reply=Xml(
                map=XmlMap(
                    fields=(XmlField("Id", source="child"), XmlField("EventsEnabled", source="child")),
                    root="GetEventsEnabledSuccess",
                )
            ),
        ),
        params=GetEventsEnabledRequest,
        result=EventsEnabledState,
        access="admin",
        effect="read",
        errors={
            10: ErrorCode("An error occurred at system level.", "internal"),
            40: ErrorCode("Invalid or no id.", "invalid_argument"),
            60: ErrorCode("Unsupported schema version.", "unsupported"),
            80: ErrorCode("Processing error.", "internal"),
            90: ErrorCode("No device.", "not_found"),
        },
    )
    set_ca_certificates = Operation(
        INFO,
        "set_ca_certificates",
        CgiBinding(
            "/axis-cgi/externalipdeviceinfo/setcacertificates.cgi",
            fixed_query=(("schemaversion", "2"),),
            args=(CgiArg("cert_ids", wire="certids", style="csv"),),
            reply=Xml(),
        ),
        params=SetCaCertificatesRequest,
        access="admin",
        effect="write",
        write="replace",
        errors={
            10: ErrorCode("An error occurred at system level.", "internal"),
            60: ErrorCode("Unsupported schema version.", "unsupported"),
            80: ErrorCode("Processing error.", "internal"),
            220: ErrorCode("Invalid CA certificate.", "invalid_argument"),
        },
    )
    get_ca_certificates = Operation(
        INFO,
        "get_ca_certificates",
        CgiBinding(
            "/axis-cgi/externalipdeviceinfo/getcacertificates.cgi",
            fixed_query=(("schemaversion", "2"),),
            reply=Xml(
                map=XmlMap(
                    fields=(XmlField("ids", source="path", name="CACertificate/Id", many=True),),
                    root="GetCACertificatesSuccess",
                )
            ),
        ),
        result=CaCertificates,
        access="admin",
        effect="read",
        errors={
            10: ErrorCode("An error occurred at system level.", "internal"),
            60: ErrorCode("Unsupported schema version.", "unsupported"),
            80: ErrorCode("Processing error.", "internal"),
        },
    )
    get_schema_versions = Operation(
        INFO,
        "get_schema_versions",
        CgiBinding(
            "/axis-cgi/externalipdeviceinfo/schemaversions.cgi",
            reply=Xml(
                map=XmlMap(
                    fields=(XmlField("versions", source="path", name="SchemaVersion/VersionNumber", many=True),),
                    root="SchemaVersionsSuccess",
                )
            ),
        ),
        result=SchemaVersions,
        access="admin",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class ExternalIpDeviceInfoApi(SyncApi):
    """External IP device information (``external-ip-device-info``)."""

    INFO = INFO

    @overload
    def create_device(
        self, request: CreateDeviceRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def create_device(
        self,
        id: str,
        /,
        *,
        description: str | MISSING = MISSING,
        serial_number: str | MISSING = MISSING,
        address: str | MISSING = MISSING,
        username: str | MISSING = MISSING,
        password: str | MISSING = MISSING,
        protocol: Protocol | MISSING = MISSING,
        certificate_validation: CertificateValidation | MISSING = MISSING,
        port: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def create_device(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Create an external IP device.

        Only id is needed; the other settings can be added later with update_device. Latest schema version
        2.1.

        Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, CreateDeviceRequest):
            kwargs = {**dict(zip(("id",), (request, *args), strict=False)), **kwargs}
            request = None
        self._run(OPS.create_device, request, kwargs, request_options)

    @overload
    def update_device(
        self, request: UpdateDeviceRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def update_device(
        self,
        id: str,
        /,
        *,
        description: str | MISSING = MISSING,
        serial_number: str | MISSING = MISSING,
        address: str | MISSING = MISSING,
        username: str | MISSING = MISSING,
        password: str | MISSING = MISSING,
        protocol: Protocol | MISSING = MISSING,
        certificate_validation: CertificateValidation | MISSING = MISSING,
        port: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def update_device(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Change settings of an existing external IP device.

        Only the given settings change. The changes take effect when the recording is restarted manually.
        Latest schema version 2.1.

        Changes only the fields given. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, UpdateDeviceRequest):
            kwargs = {**dict(zip(("id",), (request, *args), strict=False)), **kwargs}
            request = None
        self._run(OPS.update_device, request, kwargs, request_options)

    def delete_device(self, id: str, *, request_options: RequestOptions | None = None) -> None:
        """Delete an external IP device.

        Latest schema version 2.0. To delete single settings of a device, use update_device.

        Access: admin.
        """
        self._run(OPS.delete_device, None, {"id": id}, request_options)

    def list_devices(self, *, request_options: RequestOptions | None = None) -> ExternalIpDeviceList:
        """List the external IP devices.

        Latest schema version 2.1. Passwords are not returned.

        Access: admin.
        """
        return self._run(OPS.list_devices, None, {}, request_options)

    def set_events_enabled(self, id: str, enabled: bool, *, request_options: RequestOptions | None = None) -> None:
        """Enable or disable events from an external IP device.

        Supported events are VMD2, VMD3, VMD4 and VMDLite; they may not be available depending on the AXIS
        OS version or device type. Latest schema version 2.0.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_events_enabled, None, {"id": id, "enabled": enabled}, request_options)

    def get_events_enabled(self, id: str, *, request_options: RequestOptions | None = None) -> EventsEnabledState:
        """Get whether events are enabled for an external IP device.

        Latest schema version 2.0.

        Access: admin.
        """
        return self._run(OPS.get_events_enabled, None, {"id": id}, request_options)

    def set_ca_certificates(
        self, cert_ids: list[str] | MISSING = MISSING, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the CA certificates used to validate streams from external IP devices.

        The list replaces the current one; an empty list or no list unsets all CA certificates. The
        certificates must be installed first (see the certificate management API), and a CA certificate must
        be unset here before it can be uninstalled. Event streams of devices with events and certificate
        validation enabled are reset. Ongoing recordings use the new list only after a manual restart.
        Latest schema version 2.1.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        self._run(OPS.set_ca_certificates, None, {"cert_ids": cert_ids}, request_options)

    def get_ca_certificates(self, *, request_options: RequestOptions | None = None) -> CaCertificates:
        """Get the IDs of the configured CA certificates.

        Latest schema version 2.1.

        Access: admin.
        """
        return self._run(OPS.get_ca_certificates, None, {}, request_options)

    def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """List the XML schema versions supported by the product.

        Latest schema version 2.0.

        Access: admin.
        """
        return self._run(OPS.get_schema_versions, None, {}, request_options)


class AsyncExternalIpDeviceInfoApi(AsyncApi):
    """External IP device information (``external-ip-device-info``)."""

    INFO = INFO

    @overload
    async def create_device(
        self, request: CreateDeviceRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def create_device(
        self,
        id: str,
        /,
        *,
        description: str | MISSING = MISSING,
        serial_number: str | MISSING = MISSING,
        address: str | MISSING = MISSING,
        username: str | MISSING = MISSING,
        password: str | MISSING = MISSING,
        protocol: Protocol | MISSING = MISSING,
        certificate_validation: CertificateValidation | MISSING = MISSING,
        port: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def create_device(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Create an external IP device.

        Only id is needed; the other settings can be added later with update_device. Latest schema version
        2.1.

        Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, CreateDeviceRequest):
            kwargs = {**dict(zip(("id",), (request, *args), strict=False)), **kwargs}
            request = None
        await self._run(OPS.create_device, request, kwargs, request_options)

    @overload
    async def update_device(
        self, request: UpdateDeviceRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def update_device(
        self,
        id: str,
        /,
        *,
        description: str | MISSING = MISSING,
        serial_number: str | MISSING = MISSING,
        address: str | MISSING = MISSING,
        username: str | MISSING = MISSING,
        password: str | MISSING = MISSING,
        protocol: Protocol | MISSING = MISSING,
        certificate_validation: CertificateValidation | MISSING = MISSING,
        port: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def update_device(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Change settings of an existing external IP device.

        Only the given settings change. The changes take effect when the recording is restarted manually.
        Latest schema version 2.1.

        Changes only the fields given. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, UpdateDeviceRequest):
            kwargs = {**dict(zip(("id",), (request, *args), strict=False)), **kwargs}
            request = None
        await self._run(OPS.update_device, request, kwargs, request_options)

    async def delete_device(self, id: str, *, request_options: RequestOptions | None = None) -> None:
        """Delete an external IP device.

        Latest schema version 2.0. To delete single settings of a device, use update_device.

        Access: admin.
        """
        await self._run(OPS.delete_device, None, {"id": id}, request_options)

    async def list_devices(self, *, request_options: RequestOptions | None = None) -> ExternalIpDeviceList:
        """List the external IP devices.

        Latest schema version 2.1. Passwords are not returned.

        Access: admin.
        """
        return await self._run(OPS.list_devices, None, {}, request_options)

    async def set_events_enabled(
        self, id: str, enabled: bool, *, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable events from an external IP device.

        Supported events are VMD2, VMD3, VMD4 and VMDLite; they may not be available depending on the AXIS
        OS version or device type. Latest schema version 2.0.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_events_enabled, None, {"id": id, "enabled": enabled}, request_options)

    async def get_events_enabled(self, id: str, *, request_options: RequestOptions | None = None) -> EventsEnabledState:
        """Get whether events are enabled for an external IP device.

        Latest schema version 2.0.

        Access: admin.
        """
        return await self._run(OPS.get_events_enabled, None, {"id": id}, request_options)

    async def set_ca_certificates(
        self, cert_ids: list[str] | MISSING = MISSING, *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the CA certificates used to validate streams from external IP devices.

        The list replaces the current one; an empty list or no list unsets all CA certificates. The
        certificates must be installed first (see the certificate management API), and a CA certificate must
        be unset here before it can be uninstalled. Event streams of devices with events and certificate
        validation enabled are reset. Ongoing recordings use the new list only after a manual restart.
        Latest schema version 2.1.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        await self._run(OPS.set_ca_certificates, None, {"cert_ids": cert_ids}, request_options)

    async def get_ca_certificates(self, *, request_options: RequestOptions | None = None) -> CaCertificates:
        """Get the IDs of the configured CA certificates.

        Latest schema version 2.1.

        Access: admin.
        """
        return await self._run(OPS.get_ca_certificates, None, {}, request_options)

    async def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """List the XML schema versions supported by the product.

        Latest schema version 2.0.

        Access: admin.
        """
        return await self._run(OPS.get_schema_versions, None, {}, request_options)
