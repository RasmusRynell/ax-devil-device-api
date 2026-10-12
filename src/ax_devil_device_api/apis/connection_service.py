# GENERATED from specs/apis/physical-access-control/connection-service.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Door controllers can be interconnected to create door controller networks.

Docs: https://developer.axis.com/vapix/physical-access-control/connection-service/
"""

from __future__ import annotations

from typing import Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation
from .._protocols.service_json import ServiceJsonBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

PeerTrustState = Literal[
    "NotInPeerNetwork", "AddingToPeerNetwork", "InitialSyncWithPeerNetwork", "InPeerNetwork", "RemovingFromPeerNetwork"
]
PeerConnectionState = Literal["Disconnected", "PairingFailed", "Connected"]


class Peer(Model):
    """The configuration of a peer. When adding peers only ID and ExpectedAddress are given."""

    id: str | None = Field(default=None, validation_alias="ID", serialization_alias="ID")
    """MAC address in the form 000000000000 or 00:00:00:00:00:00. May be empty for pending peers."""
    expected_address: str | None = Field(
        default=None, validation_alias="ExpectedAddress", serialization_alias="ExpectedAddress"
    )
    """IPv4 address the peer was added with. May be empty for pending peers."""
    last_known_address: str | None = Field(
        default=None, validation_alias="LastKnownAddress", serialization_alias="LastKnownAddress"
    )
    """IPv4 address the peer was last discovered at. Empty if not found during discovery."""
    device_uuid: str | None = Field(default=None, validation_alias="DeviceUUID", serialization_alias="DeviceUUID")
    """Device UUID of the peer. May be empty for pending peers."""
    trust_state: PeerTrustState | None = Field(
        default=None, validation_alias="TrustState", serialization_alias="TrustState"
    )
    """Whether the peer is part of the trusted network."""
    connection_state: PeerConnectionState | None = Field(
        default=None, validation_alias="ConnectionState", serialization_alias="ConnectionState"
    )
    """Whether a network link is established to the peer."""


class PeerInfo(Model):
    """A subset of the configuration of a peer, used to identify it."""

    id: str | None = Field(default=None, validation_alias="ID", serialization_alias="ID")
    """MAC address in the form 000000000000 or 00:00:00:00:00:00."""
    expected_address: str | None = Field(
        default=None, validation_alias="ExpectedAddress", serialization_alias="ExpectedAddress"
    )
    """IPv4 address."""


class GetPeerListResult(Model):
    self_: Peer = Field(validation_alias="Self", serialization_alias="Self")
    """The door controller the call was made on."""
    peer: list[Peer] | None = Field(default=None, validation_alias="Peer", serialization_alias="Peer")
    """All connected peers and discovered but disconnected peers."""


class AddPeersRequest(Model):
    peer: list[Peer] | None = Field(default=None, validation_alias="Peer", serialization_alias="Peer")
    """Peers to add."""


class RemovePeersRequest(Model):
    peer: list[PeerInfo] = Field(validation_alias="Peer", serialization_alias="Peer", min_length=1)
    """Peers to remove."""


class SetStandAloneModeRequest(Model):
    stand_alone: bool = Field(validation_alias="StandAlone", serialization_alias="StandAlone")
    """true to refuse invitations to join a network."""


class GetStandAloneModeResult(Model):
    stand_alone: bool = Field(validation_alias="StandAlone", serialization_alias="StandAlone")
    """The stand-alone mode state."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/vapix/aconn"

INFO = ApiInfo(
    id="connection-service",
    name="Connection service",
    family=Family.SERVICE_JSON,
    docs=(
        "https://developer.axis.com/vapix/physical-access-control/connection-service/",
        "https://developer.axis.com/vapix/physical-access-control/",
        "https://developer.axis.com/vapix/physical-access-control/event-logger-service/",
        "https://developer.axis.com/vapix/physical-access-control/peripherals/",
    ),
)


class OPS:
    get_peer_list = Operation(
        INFO,
        "get_peer_list",
        ServiceJsonBinding(PATH, "aconn:GetPeerList"),
        result=GetPeerListResult,
        access="admin",
        effect="read",
    )
    add_peers = Operation(
        INFO,
        "add_peers",
        ServiceJsonBinding(PATH, "aconn:AddPeers"),
        params=AddPeersRequest,
        access="admin",
        effect="write",
        write="create",
    )
    remove_peers = Operation(
        INFO,
        "remove_peers",
        ServiceJsonBinding(PATH, "aconn:RemovePeers"),
        params=RemovePeersRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    set_stand_alone_mode = Operation(
        INFO,
        "set_stand_alone_mode",
        ServiceJsonBinding(PATH, "aconn:SetStandAloneMode"),
        params=SetStandAloneModeRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_stand_alone_mode = Operation(
        INFO,
        "get_stand_alone_mode",
        ServiceJsonBinding(PATH, "aconn:GetStandAloneMode"),
        result=GetStandAloneModeResult,
        access="admin",
        effect="read",
    )
    leave_network = Operation(
        INFO,
        "leave_network",
        ServiceJsonBinding(PATH, "aconn:LeaveNetwork"),
        access="admin",
        effect="write",
        write="delete",
    )


# ---------------------------------------------------------------------------
# API classes


class ConnectionServiceApi(SyncApi):
    """Connection service (``connection-service``)."""

    INFO = INFO

    def get_peer_list(self, *, request_options: RequestOptions | None = None) -> GetPeerListResult:
        """List the known peers of this door controller.

        Returns the peers connected in the same door controller network as well as discovered but not
        connected door controllers.

        Access: admin.
        """
        return self._run(OPS.get_peer_list, None, {}, request_options)

    @overload
    def add_peers(self, request: AddPeersRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def add_peers(
        self, /, *, peer: list[Peer] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None: ...
    def add_peers(
        self, request: AddPeersRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Invite door controllers to join this door controller's network.

        Starts an asynchronous process of inviting and adding the peers; success of the call does not mean
        the peers are added yet. An event is emitted when a connection is established. Specify
        ExpectedAddress or ID; if both are given, both must match. The majority rule applies. Joining a
        network replaces the access management configuration of the added door controller.

        Access: admin.
        """
        self._run(OPS.add_peers, request, kwargs, request_options)

    @overload
    def remove_peers(
        self, request: RemovePeersRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def remove_peers(self, /, *, peer: list[PeerInfo], request_options: RequestOptions | None = None) -> None: ...
    def remove_peers(
        self,
        request: RemovePeersRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Remove peers from the door controller network.

        Starts the removal process; success of the call does not mean the peers are removed yet. A peer
        whose ExpectedAddress or ID matches is removed (ExpectedAddress is not matched against
        LastKnownAddress). The majority rule applies, and the removed door controller ends up in stand-alone
        mode with its non-hardware configuration deleted.

        Access: admin.
        """
        self._run(OPS.remove_peers, request, kwargs, request_options)

    def set_stand_alone_mode(self, *, stand_alone: bool, request_options: RequestOptions | None = None) -> None:
        """Set whether the door controller accepts invitations to join a network.

        true means the door controller does not accept requests from peers to become part of their network;
        false means it accepts them. Already established peers are not affected.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_stand_alone_mode, None, {"stand_alone": stand_alone}, request_options)

    def get_stand_alone_mode(self, *, request_options: RequestOptions | None = None) -> GetStandAloneModeResult:
        """Return the stand-alone mode state.

        If the device is paired with any other device, this call always returns true.

        Access: admin.
        """
        return self._run(OPS.get_stand_alone_mode, None, {}, request_options)

    def leave_network(self, *, request_options: RequestOptions | None = None) -> None:
        """Leave the door controller network without contacting the other peers.

        Last-exit option for when remove_peers is not possible (for example because of the majority rule).
        Send it to the door controller that should leave. All hardware and access management configuration
        is kept; only the list of known remote door controllers is forgotten.

        Access: admin.
        """
        self._run(OPS.leave_network, None, {}, request_options)


class AsyncConnectionServiceApi(AsyncApi):
    """Connection service (``connection-service``)."""

    INFO = INFO

    async def get_peer_list(self, *, request_options: RequestOptions | None = None) -> GetPeerListResult:
        """List the known peers of this door controller.

        Returns the peers connected in the same door controller network as well as discovered but not
        connected door controllers.

        Access: admin.
        """
        return await self._run(OPS.get_peer_list, None, {}, request_options)

    @overload
    async def add_peers(
        self, request: AddPeersRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def add_peers(
        self, /, *, peer: list[Peer] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None: ...
    async def add_peers(
        self, request: AddPeersRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Invite door controllers to join this door controller's network.

        Starts an asynchronous process of inviting and adding the peers; success of the call does not mean
        the peers are added yet. An event is emitted when a connection is established. Specify
        ExpectedAddress or ID; if both are given, both must match. The majority rule applies. Joining a
        network replaces the access management configuration of the added door controller.

        Access: admin.
        """
        await self._run(OPS.add_peers, request, kwargs, request_options)

    @overload
    async def remove_peers(
        self, request: RemovePeersRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def remove_peers(self, /, *, peer: list[PeerInfo], request_options: RequestOptions | None = None) -> None: ...
    async def remove_peers(
        self,
        request: RemovePeersRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Remove peers from the door controller network.

        Starts the removal process; success of the call does not mean the peers are removed yet. A peer
        whose ExpectedAddress or ID matches is removed (ExpectedAddress is not matched against
        LastKnownAddress). The majority rule applies, and the removed door controller ends up in stand-alone
        mode with its non-hardware configuration deleted.

        Access: admin.
        """
        await self._run(OPS.remove_peers, request, kwargs, request_options)

    async def set_stand_alone_mode(self, *, stand_alone: bool, request_options: RequestOptions | None = None) -> None:
        """Set whether the door controller accepts invitations to join a network.

        true means the door controller does not accept requests from peers to become part of their network;
        false means it accepts them. Already established peers are not affected.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_stand_alone_mode, None, {"stand_alone": stand_alone}, request_options)

    async def get_stand_alone_mode(self, *, request_options: RequestOptions | None = None) -> GetStandAloneModeResult:
        """Return the stand-alone mode state.

        If the device is paired with any other device, this call always returns true.

        Access: admin.
        """
        return await self._run(OPS.get_stand_alone_mode, None, {}, request_options)

    async def leave_network(self, *, request_options: RequestOptions | None = None) -> None:
        """Leave the door controller network without contacting the other peers.

        Last-exit option for when remove_peers is not possible (for example because of the majority rule).
        Send it to the door controller that should leave. All hardware and access management configuration
        is kept; only the list of known remote door controllers is forgotten.

        Access: admin.
        """
        await self._run(OPS.leave_network, None, {}, request_options)
