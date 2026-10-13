# GENERATED from specs/apis/device-configuration/camera-pairing-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Pair the device to an external camera to view the camera's video on the device.

Docs: https://developer.axis.com/vapix/device-configuration/edge-to-edge-camera-pairing-api/
"""

from __future__ import annotations

from typing import Annotated, Any, ClassVar, Literal, overload

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, ErrorCode, Family, Model, Operation, not_sent
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

Address = Annotated[str, Field(max_length=64)]
CameraPairingStatus = Literal["NOT_PAIRED", "PAIRED", "ERROR", "CONNECTING"]
CameraPairingStreamingProtocol = Literal["RTSP", "SRTSP"]
Description = Annotated[str, Field(max_length=128)]
ID = Annotated[str, Field(max_length=64)]
Password = Annotated[str, Field(max_length=64)]
ProductModel = Annotated[str, Field(max_length=64)]
ProductName = Annotated[str, Field(max_length=64)]
SelectedVideoChannel = Annotated[str, Field(max_length=64)]
Username = Annotated[str, Field(max_length=64)]
VideoChannels = list[str]


class Pairing(Model):
    """A camera pairing. The password is never returned."""

    __response_required__: ClassVar[frozenset[str]] = frozenset({"id"})
    __read_only__: ClassVar[frozenset[str]] = frozenset(
        {"id", "product_model", "product_name", "status", "video_channels"}
    )
    address: Address | None = None
    """Address for the camera pairing."""
    description: Description | None = None
    """Description of the paired camera."""
    id: ID = Field(default_factory=not_sent)
    """The unique ID generated automatically for the camera pairing."""
    product_model: ProductModel | None = Field(
        default=None, validation_alias="productModel", serialization_alias="productModel"
    )
    """The product model of the paired camera."""
    product_name: ProductName | None = Field(
        default=None, validation_alias="productName", serialization_alias="productName"
    )
    """The full product name of the paired camera."""
    selected_video_channel: SelectedVideoChannel | None = Field(
        default=None, validation_alias="selectedVideoChannel", serialization_alias="selectedVideoChannel"
    )
    """Video Channel to pull the stream from on the paired camera."""
    status: CameraPairingStatus | None = None
    """Current status of the camera pairing."""
    streaming_protocol: CameraPairingStreamingProtocol | None = Field(
        default=None, validation_alias="streamingProtocol", serialization_alias="streamingProtocol"
    )
    username: Username | None = None
    """Username for the camera pairing."""
    verify_certificate: bool | None = Field(
        default=None, validation_alias="verifyCertificate", serialization_alias="verifyCertificate"
    )
    """Indicates whether to verify the certificates. It is only useful when `streamingProtocol` is set to `SRTSP`."""
    video_channels: VideoChannels | None = Field(
        default=None, validation_alias="videoChannels", serialization_alias="videoChannels"
    )
    """Video channels available on the paired camera."""


class CameraPairing(Model):
    """The whole API tree."""

    camera_pairings: list[Pairing] | None = Field(
        default=None, validation_alias="cameraPairings", serialization_alias="cameraPairings"
    )


class AddCameraPairingRequest(Model):
    """Arguments of ``add_camera_pairing``."""

    address: Address
    """Address for the camera pairing."""
    username: Username
    """Username for the camera pairing."""
    password: Password
    """Password for the camera pairing."""
    streaming_protocol: CameraPairingStreamingProtocol = Field(
        validation_alias="streamingProtocol", serialization_alias="streamingProtocol"
    )
    verify_certificate: bool = Field(validation_alias="verifyCertificate", serialization_alias="verifyCertificate")
    """Indicates whether to verify the certificates. It is only useful when `streamingProtocol` is set to `SRTSP`."""
    description: Description
    """Description of the paired camera."""


class PairingIdRequest(Model):
    id: ID


class SetCameraPairingAddressRequest(Model):
    id: ID
    address: Address
    """Address for the camera pairing."""


class SetCameraPairingDescriptionRequest(Model):
    id: ID
    description: Description
    """Description of the paired camera."""


class SetCameraPairingPasswordRequest(Model):
    id: ID
    password: Password
    """Password for the camera pairing."""


class SetCameraPairingSelectedVideoChannelRequest(Model):
    id: ID
    selected_video_channel: SelectedVideoChannel = Field(
        validation_alias="selectedVideoChannel", serialization_alias="selectedVideoChannel"
    )
    """Video Channel to pull the stream from on the paired camera."""


class SetCameraPairingStreamingProtocolRequest(Model):
    id: ID
    streaming_protocol: CameraPairingStreamingProtocol = Field(
        validation_alias="streamingProtocol", serialization_alias="streamingProtocol"
    )


class SetCameraPairingUsernameRequest(Model):
    id: ID
    username: Username
    """Username for the camera pairing."""


class SetCameraPairingVerifyCertificateRequest(Model):
    id: ID
    verify_certificate: bool = Field(validation_alias="verifyCertificate", serialization_alias="verifyCertificate")
    """Indicates whether to verify the certificates. It is only useful when `streamingProtocol` is set to `SRTSP`."""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/camera-pairing/v1"

INFO = ApiInfo(
    id="camera-pairing-config",
    name="Edge-to-edge camera pairing API",
    family=Family.DCA,
    discovery=(DcaDiscovery("camera-pairing", "v1"),),
    docs=("https://developer.axis.com/vapix/device-configuration/edge-to-edge-camera-pairing-api/",),
    errors={
        101: ErrorCode(
            "The specified address is already assigned to the device itself. Occurs when you try to create a camera pairing to the device itself.",
            "invalid_argument",
        ),
        102: ErrorCode(
            "The specified address is not valid. Occurs when the specified address is not a valid IPv4/IPv6 address or a DNS name.",
            "invalid_argument",
        ),
        104: ErrorCode(
            "Maximum number of camera pairings reached. Occurs when you try to create a second camera pairing."
        ),
        106: ErrorCode("Lost connection. The streaming connection is lost.", "unavailable"),
        107: ErrorCode("Unauthorized. Unauthorized streaming.", "access_denied"),
        108: ErrorCode("Could not connect. Could not connect to streaming.", "unavailable"),
    },
)


class OPS:
    get_all = Operation(INFO, "get_all", DcaBinding("GET", ROOT), result=CameraPairing, access="admin", effect="read")
    list_camera_pairings = Operation(
        INFO,
        "list_camera_pairings",
        DcaBinding("GET", f"{ROOT}/cameraPairings"),
        result=list[Pairing],
        access="admin",
        effect="read",
    )
    get_camera_pairing = Operation(
        INFO,
        "get_camera_pairing",
        DcaBinding("GET", f"{ROOT}/cameraPairings/{{id}}"),
        params=PairingIdRequest,
        result=Pairing,
        access="admin",
        effect="read",
    )
    add_camera_pairing = Operation(
        INFO,
        "add_camera_pairing",
        DcaBinding("POST", f"{ROOT}/cameraPairings", body="object"),
        params=AddCameraPairingRequest,
        result=Pairing,
        access="admin",
        effect="write",
        write="create",
        errors={
            101: ErrorCode("The address belongs to the device itself."),
            104: ErrorCode("A camera pairing already exists."),
        },
    )
    get_camera_pairing_status = Operation(
        INFO,
        "get_camera_pairing_status",
        DcaBinding("GET", f"{ROOT}/cameraPairings/{{id}}/status"),
        params=PairingIdRequest,
        result=CameraPairingStatus,
        access="admin",
        effect="read",
    )
    remove_camera_pairing = Operation(
        INFO,
        "remove_camera_pairing",
        DcaBinding("DELETE", f"{ROOT}/cameraPairings/{{id}}"),
        params=PairingIdRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    set_camera_pairing_address = Operation(
        INFO,
        "set_camera_pairing_address",
        DcaBinding("PATCH", f"{ROOT}/cameraPairings/{{id}}/address", body="value", body_field="address"),
        params=SetCameraPairingAddressRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_camera_pairing_description = Operation(
        INFO,
        "set_camera_pairing_description",
        DcaBinding("PATCH", f"{ROOT}/cameraPairings/{{id}}/description", body="value", body_field="description"),
        params=SetCameraPairingDescriptionRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_camera_pairing_password = Operation(
        INFO,
        "set_camera_pairing_password",
        DcaBinding("PATCH", f"{ROOT}/cameraPairings/{{id}}/password", body="value", body_field="password"),
        params=SetCameraPairingPasswordRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_camera_pairing_selected_video_channel = Operation(
        INFO,
        "set_camera_pairing_selected_video_channel",
        DcaBinding(
            "PATCH",
            f"{ROOT}/cameraPairings/{{id}}/selectedVideoChannel",
            body="value",
            body_field="selectedVideoChannel",
        ),
        params=SetCameraPairingSelectedVideoChannelRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_camera_pairing_streaming_protocol = Operation(
        INFO,
        "set_camera_pairing_streaming_protocol",
        DcaBinding(
            "PATCH", f"{ROOT}/cameraPairings/{{id}}/streamingProtocol", body="value", body_field="streamingProtocol"
        ),
        params=SetCameraPairingStreamingProtocolRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_camera_pairing_username = Operation(
        INFO,
        "set_camera_pairing_username",
        DcaBinding("PATCH", f"{ROOT}/cameraPairings/{{id}}/username", body="value", body_field="username"),
        params=SetCameraPairingUsernameRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_camera_pairing_verify_certificate = Operation(
        INFO,
        "set_camera_pairing_verify_certificate",
        DcaBinding(
            "PATCH", f"{ROOT}/cameraPairings/{{id}}/verifyCertificate", body="value", body_field="verifyCertificate"
        ),
        params=SetCameraPairingVerifyCertificateRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class CameraPairingApi(SyncApi):
    """Edge-to-edge camera pairing API (``camera-pairing-config``, v1)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> CameraPairing:
        """The whole camera pairing tree. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    def list_camera_pairings(self, *, request_options: RequestOptions | None = None) -> list[Pairing]:
        """List the camera pairings. Access: admin."""
        return self._run(OPS.list_camera_pairings, None, {}, request_options)

    def get_camera_pairing(self, id: ID, *, request_options: RequestOptions | None = None) -> Pairing:
        """One camera pairing. Access: admin."""
        return self._run(OPS.get_camera_pairing, None, {"id": id}, request_options)

    @overload
    def add_camera_pairing(
        self, request: AddCameraPairingRequest, /, *, request_options: RequestOptions | None = None
    ) -> Pairing: ...
    @overload
    def add_camera_pairing(
        self,
        /,
        *,
        address: Address,
        username: Username,
        password: Password,
        streaming_protocol: CameraPairingStreamingProtocol,
        verify_certificate: bool,
        description: Description,
        request_options: RequestOptions | None = None,
    ) -> Pairing: ...
    def add_camera_pairing(
        self,
        request: AddCameraPairingRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> Pairing:
        """Pair an external camera to the device.

        Only one camera pairing can exist at a time (error 104).

        Access: admin.
        """
        return self._run(OPS.add_camera_pairing, request, kwargs, request_options)

    def get_camera_pairing_status(
        self, id: ID, *, request_options: RequestOptions | None = None
    ) -> CameraPairingStatus:
        """The current status of a camera pairing.

        When the status is ``ERROR``, read the pairing with ``get_camera_pairing`` for more information.

        Access: admin.
        """
        return self._run(OPS.get_camera_pairing_status, None, {"id": id}, request_options)

    def remove_camera_pairing(self, id: ID, *, request_options: RequestOptions | None = None) -> None:
        """Unpair an external camera from the device. Access: admin."""
        self._run(OPS.remove_camera_pairing, None, {"id": id}, request_options)

    def set_camera_pairing_address(
        self, id: ID, *, address: Address, request_options: RequestOptions | None = None
    ) -> None:
        """Set the address of a camera pairing. Changes only the fields given. Access: admin."""
        self._run(OPS.set_camera_pairing_address, None, {"id": id, "address": address}, request_options)

    def set_camera_pairing_description(
        self, id: ID, *, description: Description, request_options: RequestOptions | None = None
    ) -> None:
        """Set the description of a camera pairing. Changes only the fields given. Access: admin."""
        self._run(OPS.set_camera_pairing_description, None, {"id": id, "description": description}, request_options)

    def set_camera_pairing_password(
        self, id: ID, *, password: Password, request_options: RequestOptions | None = None
    ) -> None:
        """Set the password of a camera pairing. Changes only the fields given. Access: admin."""
        self._run(OPS.set_camera_pairing_password, None, {"id": id, "password": password}, request_options)

    def set_camera_pairing_selected_video_channel(
        self, id: ID, *, selected_video_channel: SelectedVideoChannel, request_options: RequestOptions | None = None
    ) -> None:
        """Set the selected video channel of a camera pairing.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_camera_pairing_selected_video_channel,
            None,
            {"id": id, "selected_video_channel": selected_video_channel},
            request_options,
        )

    def set_camera_pairing_streaming_protocol(
        self,
        id: ID,
        *,
        streaming_protocol: CameraPairingStreamingProtocol,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the streaming protocol of a camera pairing.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_camera_pairing_streaming_protocol,
            None,
            {"id": id, "streaming_protocol": streaming_protocol},
            request_options,
        )

    def set_camera_pairing_username(
        self, id: ID, *, username: Username, request_options: RequestOptions | None = None
    ) -> None:
        """Set the username of a camera pairing. Changes only the fields given. Access: admin."""
        self._run(OPS.set_camera_pairing_username, None, {"id": id, "username": username}, request_options)

    def set_camera_pairing_verify_certificate(
        self, id: ID, *, verify_certificate: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Set the verify certificate of a camera pairing.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_camera_pairing_verify_certificate,
            None,
            {"id": id, "verify_certificate": verify_certificate},
            request_options,
        )


class AsyncCameraPairingApi(AsyncApi):
    """Edge-to-edge camera pairing API (``camera-pairing-config``, v1)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> CameraPairing:
        """The whole camera pairing tree. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def list_camera_pairings(self, *, request_options: RequestOptions | None = None) -> list[Pairing]:
        """List the camera pairings. Access: admin."""
        return await self._run(OPS.list_camera_pairings, None, {}, request_options)

    async def get_camera_pairing(self, id: ID, *, request_options: RequestOptions | None = None) -> Pairing:
        """One camera pairing. Access: admin."""
        return await self._run(OPS.get_camera_pairing, None, {"id": id}, request_options)

    @overload
    async def add_camera_pairing(
        self, request: AddCameraPairingRequest, /, *, request_options: RequestOptions | None = None
    ) -> Pairing: ...
    @overload
    async def add_camera_pairing(
        self,
        /,
        *,
        address: Address,
        username: Username,
        password: Password,
        streaming_protocol: CameraPairingStreamingProtocol,
        verify_certificate: bool,
        description: Description,
        request_options: RequestOptions | None = None,
    ) -> Pairing: ...
    async def add_camera_pairing(
        self,
        request: AddCameraPairingRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> Pairing:
        """Pair an external camera to the device.

        Only one camera pairing can exist at a time (error 104).

        Access: admin.
        """
        return await self._run(OPS.add_camera_pairing, request, kwargs, request_options)

    async def get_camera_pairing_status(
        self, id: ID, *, request_options: RequestOptions | None = None
    ) -> CameraPairingStatus:
        """The current status of a camera pairing.

        When the status is ``ERROR``, read the pairing with ``get_camera_pairing`` for more information.

        Access: admin.
        """
        return await self._run(OPS.get_camera_pairing_status, None, {"id": id}, request_options)

    async def remove_camera_pairing(self, id: ID, *, request_options: RequestOptions | None = None) -> None:
        """Unpair an external camera from the device. Access: admin."""
        await self._run(OPS.remove_camera_pairing, None, {"id": id}, request_options)

    async def set_camera_pairing_address(
        self, id: ID, *, address: Address, request_options: RequestOptions | None = None
    ) -> None:
        """Set the address of a camera pairing. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_camera_pairing_address, None, {"id": id, "address": address}, request_options)

    async def set_camera_pairing_description(
        self, id: ID, *, description: Description, request_options: RequestOptions | None = None
    ) -> None:
        """Set the description of a camera pairing. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_camera_pairing_description, None, {"id": id, "description": description}, request_options
        )

    async def set_camera_pairing_password(
        self, id: ID, *, password: Password, request_options: RequestOptions | None = None
    ) -> None:
        """Set the password of a camera pairing. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_camera_pairing_password, None, {"id": id, "password": password}, request_options)

    async def set_camera_pairing_selected_video_channel(
        self, id: ID, *, selected_video_channel: SelectedVideoChannel, request_options: RequestOptions | None = None
    ) -> None:
        """Set the selected video channel of a camera pairing.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_camera_pairing_selected_video_channel,
            None,
            {"id": id, "selected_video_channel": selected_video_channel},
            request_options,
        )

    async def set_camera_pairing_streaming_protocol(
        self,
        id: ID,
        *,
        streaming_protocol: CameraPairingStreamingProtocol,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the streaming protocol of a camera pairing.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_camera_pairing_streaming_protocol,
            None,
            {"id": id, "streaming_protocol": streaming_protocol},
            request_options,
        )

    async def set_camera_pairing_username(
        self, id: ID, *, username: Username, request_options: RequestOptions | None = None
    ) -> None:
        """Set the username of a camera pairing. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_camera_pairing_username, None, {"id": id, "username": username}, request_options)

    async def set_camera_pairing_verify_certificate(
        self, id: ID, *, verify_certificate: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Set the verify certificate of a camera pairing.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_camera_pairing_verify_certificate,
            None,
            {"id": id, "verify_certificate": verify_certificate},
            request_options,
        )
