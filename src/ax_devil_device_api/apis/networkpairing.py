# GENERATED from specs/apis/device-configuration/networkpairing-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Pair the device with remote Axis devices (edge-to-edge) and use their capabilities, such as sirens and lights.

Docs: https://developer.axis.com/vapix/device-configuration/network-pairing-api/
"""

from __future__ import annotations

from typing import Annotated, Any, ClassVar, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation, not_sent
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

ConnectionStatus = Literal["connected", "disconnected", "error_unknown", "error_authentication", "error_certificate"]
PairingDescription = Annotated[str, Field(max_length=200)]
PairingId = Annotated[str, Field(pattern="^[1-9][0-9]*$")]
PairingNiceName = Annotated[str, Field(max_length=50)]
SirenLightKind = Literal["siren", "light"]


class Capability(Model):
    """A capability of a feature on a paired device."""

    __response_required__: ClassVar[frozenset[str]] = frozenset({"name"})
    __read_only__: ClassVar[frozenset[str]] = frozenset({"name"})
    enabled: bool | None = None
    """The capability is administratively enabled on the host. Toggling it does not affect the remote device."""
    name: str = Field(default_factory=not_sent)
    """Name of a pairing capability."""


class Feature(Model):
    """A category of capabilities provided by a pairing."""

    __response_required__: ClassVar[frozenset[str]] = frozenset({"category"})
    __read_only__: ClassVar[frozenset[str]] = frozenset({"category"})
    category: str = Field(default_factory=not_sent)
    """The capability category name, for example SirenLight."""
    capabilities: list[Capability] | None = None


class Pairing(Model):
    """A configured pairing with a remote device. The password is never returned."""

    __response_required__: ClassVar[frozenset[str]] = frozenset({"id"})
    __read_only__: ClassVar[frozenset[str]] = frozenset(
        {"address", "connection_status", "features", "id", "model_name", "username"}
    )
    id: PairingId = Field(default_factory=not_sent)
    """The pairing identifier."""
    address: str | None = None
    """The network address of the remote device. Must be a FQDN DNS name, an IPv4 address (dotted quad notation), or an IPv6 address."""
    username: str | None = None
    """The name of the user account on the remote device to use when accessing it."""
    description: PairingDescription | None = None
    """Description of the pairing."""
    nice_name: PairingNiceName | None = None
    """Short, user friendly, name of a pairing."""
    model_name: str | None = None
    """The detected model name of the remote device."""
    connection_status: ConnectionStatus | None = None
    """Connectivity status of the remote device."""
    features: list[Feature] | None = None


class SirenLightCapability(Model):
    """Capabilities of a paired siren/light device."""

    pairing_id: PairingId | None = None
    """Unique identifier of a pairing."""
    supported: list[SirenLightKind] | None = None
    """Capabilities supported by the remote device; one or both of siren and light."""


class SirenLightProfile(Model):
    """The siren/light profiles available on a paired device."""

    names: list[str] | None = None
    """Profile names."""
    pairing: PairingId
    """The pairing providing the profiles."""


class SirenLight(Model):
    """Siren/light plugin."""

    capabilities: list[SirenLightCapability] | None = None
    profiles: list[SirenLightProfile] | None = None


class Plugins(Model):
    """Plugins loaded on the device."""

    siren_light_supported: bool | None = None
    """Whether the siren/light plugin is supported on this device."""
    siren_light: SirenLight | None = None


class Networkpairing(Model):
    """The whole API tree."""

    pairings: list[Pairing] | None = None
    plugins: Plugins | None = None


class AddPairingRequest(Model):
    """Arguments of ``add_pairing``. The remote device's certificate is pinned during pairing, and all features start enabled."""

    __masked__: ClassVar[frozenset[str]] = frozenset({"password"})
    address: str
    """The network address of the remote device. Must be a FQDN DNS name, an IPv4 address (dotted quad notation), or an IPv6 address."""
    username: str
    """The name of the user account on the remote device to use when accessing it."""
    password: str
    """The password of the user account on the remote device. It can be updated but never read."""
    certificate_common_name: str | None = None
    """Common name expected in the remote device certificate."""
    description: PairingDescription | None = None
    """Description of the pairing."""
    nice_name: PairingNiceName | None = None
    """Short, user friendly, name of a pairing."""


class PairingIdRequest(Model):
    id: PairingId


class SetPairingDescriptionRequest(Model):
    id: PairingId
    description: PairingDescription


class SetPairingNiceNameRequest(Model):
    id: PairingId
    nice_name: PairingNiceName


class FeatureRequest(Model):
    id: PairingId
    category: str
    """The capability category name, for example SirenLight."""


class CapabilityRequest(Model):
    id: PairingId
    category: str
    """The capability category name, for example SirenLight."""
    name: str
    """Name of a pairing capability."""


class SetCapabilityEnabledRequest(Model):
    id: PairingId
    category: str
    """The capability category name, for example SirenLight."""
    name: str
    """Name of a pairing capability."""
    enabled: bool


class PairingKeyRequest(Model):
    pairing: PairingId


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/networkpairing/v1beta"

INFO = ApiInfo(
    id="networkpairing-config",
    name="Network pairing",
    family=Family.DCA,
    discovery=(DcaDiscovery("networkpairing", "v1"),),
    status="beta",
    docs=("https://developer.axis.com/vapix/device-configuration/network-pairing-api/",),
)


class OPS:
    get_all = Operation(INFO, "get_all", DcaBinding("GET", ROOT), result=Networkpairing, access="admin", effect="read")
    list_pairings = Operation(
        INFO,
        "list_pairings",
        DcaBinding("GET", f"{ROOT}/pairings"),
        result=list[Pairing],
        access="admin",
        effect="read",
    )
    get_pairing = Operation(
        INFO,
        "get_pairing",
        DcaBinding("GET", f"{ROOT}/pairings/{{id}}"),
        params=PairingIdRequest,
        result=Pairing,
        access="admin",
        effect="read",
    )
    add_pairing = Operation(
        INFO,
        "add_pairing",
        DcaBinding("POST", f"{ROOT}/pairings", body="object"),
        params=AddPairingRequest,
        result=Pairing,
        access="admin",
        effect="write",
        write="create",
    )
    remove_pairing = Operation(
        INFO,
        "remove_pairing",
        DcaBinding("DELETE", f"{ROOT}/pairings/{{id}}"),
        params=PairingIdRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    set_pairing_description = Operation(
        INFO,
        "set_pairing_description",
        DcaBinding("PATCH", f"{ROOT}/pairings/{{id}}/description", body="value", body_field="description"),
        params=SetPairingDescriptionRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_pairing_nice_name = Operation(
        INFO,
        "set_pairing_nice_name",
        DcaBinding("PATCH", f"{ROOT}/pairings/{{id}}/nice_name", body="value", body_field="nice_name"),
        params=SetPairingNiceNameRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    list_features = Operation(
        INFO,
        "list_features",
        DcaBinding("GET", f"{ROOT}/pairings/{{id}}/features"),
        params=PairingIdRequest,
        result=list[Feature],
        access="admin",
        effect="read",
    )
    get_feature = Operation(
        INFO,
        "get_feature",
        DcaBinding("GET", f"{ROOT}/pairings/{{id}}/features/{{category}}"),
        params=FeatureRequest,
        result=Feature,
        access="admin",
        effect="read",
    )
    list_capabilities = Operation(
        INFO,
        "list_capabilities",
        DcaBinding("GET", f"{ROOT}/pairings/{{id}}/features/{{category}}/capabilities"),
        params=FeatureRequest,
        result=list[Capability],
        access="admin",
        effect="read",
    )
    get_capability = Operation(
        INFO,
        "get_capability",
        DcaBinding("GET", f"{ROOT}/pairings/{{id}}/features/{{category}}/capabilities/{{name}}"),
        params=CapabilityRequest,
        result=Capability,
        access="admin",
        effect="read",
    )
    set_capability_enabled = Operation(
        INFO,
        "set_capability_enabled",
        DcaBinding(
            "PATCH",
            f"{ROOT}/pairings/{{id}}/features/{{category}}/capabilities/{{name}}/enabled",
            body="value",
            body_field="enabled",
        ),
        params=SetCapabilityEnabledRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_plugins = Operation(
        INFO, "get_plugins", DcaBinding("GET", f"{ROOT}/plugins"), result=Plugins, access="admin", effect="read"
    )
    get_siren_light_supported = Operation(
        INFO,
        "get_siren_light_supported",
        DcaBinding("GET", f"{ROOT}/plugins/siren_light_supported"),
        result=bool,
        access="admin",
        effect="read",
    )
    get_siren_light = Operation(
        INFO,
        "get_siren_light",
        DcaBinding("GET", f"{ROOT}/plugins/siren_light"),
        result=SirenLight,
        access="admin",
        effect="read",
    )
    list_siren_light_capabilities = Operation(
        INFO,
        "list_siren_light_capabilities",
        DcaBinding("GET", f"{ROOT}/plugins/siren_light/capabilities"),
        result=list[SirenLightCapability],
        access="admin",
        effect="read",
    )
    get_siren_light_capability = Operation(
        INFO,
        "get_siren_light_capability",
        DcaBinding("GET", f"{ROOT}/plugins/siren_light/capabilities/{{pairing}}"),
        params=PairingKeyRequest,
        result=SirenLightCapability,
        access="admin",
        effect="read",
    )
    list_siren_light_profiles = Operation(
        INFO,
        "list_siren_light_profiles",
        DcaBinding("GET", f"{ROOT}/plugins/siren_light/profiles"),
        result=list[SirenLightProfile],
        access="admin",
        effect="read",
    )
    get_siren_light_profile = Operation(
        INFO,
        "get_siren_light_profile",
        DcaBinding("GET", f"{ROOT}/plugins/siren_light/profiles/{{pairing}}"),
        params=PairingKeyRequest,
        result=SirenLightProfile,
        access="admin",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class NetworkpairingApi(SyncApi):
    """Network pairing (``networkpairing-config``, v1)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> Networkpairing:
        """All pairings and plugin information. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    def list_pairings(self, *, request_options: RequestOptions | None = None) -> list[Pairing]:
        """List the pairings. Access: admin."""
        return self._run(OPS.list_pairings, None, {}, request_options)

    def get_pairing(self, id: PairingId, *, request_options: RequestOptions | None = None) -> Pairing:
        """Get one pairing. Access: admin."""
        return self._run(OPS.get_pairing, None, {"id": id}, request_options)

    @overload
    def add_pairing(
        self, request: AddPairingRequest, /, *, request_options: RequestOptions | None = None
    ) -> Pairing: ...
    @overload
    def add_pairing(
        self,
        /,
        *,
        address: str,
        username: str,
        password: str,
        certificate_common_name: str | MISSING = MISSING,
        description: PairingDescription | MISSING = MISSING,
        nice_name: PairingNiceName | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> Pairing: ...
    def add_pairing(
        self,
        request: AddPairingRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> Pairing:
        """Add a pairing with a remote device.

        The request carries the remote device's credentials, so use a secured channel. The response is the
        created pairing.

        Access: admin.
        """
        return self._run(OPS.add_pairing, request, kwargs, request_options)

    def remove_pairing(self, id: PairingId, *, request_options: RequestOptions | None = None) -> None:
        """Remove a pairing. Access: admin."""
        self._run(OPS.remove_pairing, None, {"id": id}, request_options)

    def set_pairing_description(
        self, id: PairingId, *, description: PairingDescription, request_options: RequestOptions | None = None
    ) -> None:
        """Set the description of a pairing. Changes only the fields given. Access: admin."""
        self._run(OPS.set_pairing_description, None, {"id": id, "description": description}, request_options)

    def set_pairing_nice_name(
        self, id: PairingId, *, nice_name: PairingNiceName, request_options: RequestOptions | None = None
    ) -> None:
        """Set the nice name of a pairing. Changes only the fields given. Access: admin."""
        self._run(OPS.set_pairing_nice_name, None, {"id": id, "nice_name": nice_name}, request_options)

    def list_features(self, id: PairingId, *, request_options: RequestOptions | None = None) -> list[Feature]:
        """List the features a pairing provides. Access: admin."""
        return self._run(OPS.list_features, None, {"id": id}, request_options)

    def get_feature(self, id: PairingId, category: str, *, request_options: RequestOptions | None = None) -> Feature:
        """Get one feature of a pairing. Access: admin."""
        return self._run(OPS.get_feature, None, {"id": id, "category": category}, request_options)

    def list_capabilities(
        self, id: PairingId, category: str, *, request_options: RequestOptions | None = None
    ) -> list[Capability]:
        """List the capabilities of a feature. Access: admin."""
        return self._run(OPS.list_capabilities, None, {"id": id, "category": category}, request_options)

    def get_capability(
        self, id: PairingId, category: str, name: str, *, request_options: RequestOptions | None = None
    ) -> Capability:
        """Get one capability of a feature. Access: admin."""
        return self._run(OPS.get_capability, None, {"id": id, "category": category, "name": name}, request_options)

    def set_capability_enabled(
        self, id: PairingId, category: str, name: str, *, enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable a capability of a pairing on this device.

        Only affects whether the feature is usable on the host, not the remote device.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_capability_enabled,
            None,
            {"id": id, "category": category, "name": name, "enabled": enabled},
            request_options,
        )

    def get_plugins(self, *, request_options: RequestOptions | None = None) -> Plugins:
        """Get the plugin information. Access: admin."""
        return self._run(OPS.get_plugins, None, {}, request_options)

    def get_siren_light_supported(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether the siren/light plugin is supported on this device.

        Check this before using the siren/light plugin operations.

        Access: admin.
        """
        return self._run(OPS.get_siren_light_supported, None, {}, request_options)

    def get_siren_light(self, *, request_options: RequestOptions | None = None) -> SirenLight:
        """Get the siren/light plugin information. Access: admin."""
        return self._run(OPS.get_siren_light, None, {}, request_options)

    def list_siren_light_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> list[SirenLightCapability]:
        """List the siren/light capabilities of the paired devices. Access: admin."""
        return self._run(OPS.list_siren_light_capabilities, None, {}, request_options)

    def get_siren_light_capability(
        self, pairing: PairingId, *, request_options: RequestOptions | None = None
    ) -> SirenLightCapability:
        """Get the siren/light capabilities of one paired device. Access: admin."""
        return self._run(OPS.get_siren_light_capability, None, {"pairing": pairing}, request_options)

    def list_siren_light_profiles(self, *, request_options: RequestOptions | None = None) -> list[SirenLightProfile]:
        """List the siren/light profiles of the paired devices. Access: admin."""
        return self._run(OPS.list_siren_light_profiles, None, {}, request_options)

    def get_siren_light_profile(
        self, pairing: PairingId, *, request_options: RequestOptions | None = None
    ) -> SirenLightProfile:
        """List the profiles that can be started or stopped on one paired device. Access: admin."""
        return self._run(OPS.get_siren_light_profile, None, {"pairing": pairing}, request_options)


class AsyncNetworkpairingApi(AsyncApi):
    """Network pairing (``networkpairing-config``, v1)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> Networkpairing:
        """All pairings and plugin information. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def list_pairings(self, *, request_options: RequestOptions | None = None) -> list[Pairing]:
        """List the pairings. Access: admin."""
        return await self._run(OPS.list_pairings, None, {}, request_options)

    async def get_pairing(self, id: PairingId, *, request_options: RequestOptions | None = None) -> Pairing:
        """Get one pairing. Access: admin."""
        return await self._run(OPS.get_pairing, None, {"id": id}, request_options)

    @overload
    async def add_pairing(
        self, request: AddPairingRequest, /, *, request_options: RequestOptions | None = None
    ) -> Pairing: ...
    @overload
    async def add_pairing(
        self,
        /,
        *,
        address: str,
        username: str,
        password: str,
        certificate_common_name: str | MISSING = MISSING,
        description: PairingDescription | MISSING = MISSING,
        nice_name: PairingNiceName | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> Pairing: ...
    async def add_pairing(
        self,
        request: AddPairingRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> Pairing:
        """Add a pairing with a remote device.

        The request carries the remote device's credentials, so use a secured channel. The response is the
        created pairing.

        Access: admin.
        """
        return await self._run(OPS.add_pairing, request, kwargs, request_options)

    async def remove_pairing(self, id: PairingId, *, request_options: RequestOptions | None = None) -> None:
        """Remove a pairing. Access: admin."""
        await self._run(OPS.remove_pairing, None, {"id": id}, request_options)

    async def set_pairing_description(
        self, id: PairingId, *, description: PairingDescription, request_options: RequestOptions | None = None
    ) -> None:
        """Set the description of a pairing. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_pairing_description, None, {"id": id, "description": description}, request_options)

    async def set_pairing_nice_name(
        self, id: PairingId, *, nice_name: PairingNiceName, request_options: RequestOptions | None = None
    ) -> None:
        """Set the nice name of a pairing. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_pairing_nice_name, None, {"id": id, "nice_name": nice_name}, request_options)

    async def list_features(self, id: PairingId, *, request_options: RequestOptions | None = None) -> list[Feature]:
        """List the features a pairing provides. Access: admin."""
        return await self._run(OPS.list_features, None, {"id": id}, request_options)

    async def get_feature(
        self, id: PairingId, category: str, *, request_options: RequestOptions | None = None
    ) -> Feature:
        """Get one feature of a pairing. Access: admin."""
        return await self._run(OPS.get_feature, None, {"id": id, "category": category}, request_options)

    async def list_capabilities(
        self, id: PairingId, category: str, *, request_options: RequestOptions | None = None
    ) -> list[Capability]:
        """List the capabilities of a feature. Access: admin."""
        return await self._run(OPS.list_capabilities, None, {"id": id, "category": category}, request_options)

    async def get_capability(
        self, id: PairingId, category: str, name: str, *, request_options: RequestOptions | None = None
    ) -> Capability:
        """Get one capability of a feature. Access: admin."""
        return await self._run(
            OPS.get_capability, None, {"id": id, "category": category, "name": name}, request_options
        )

    async def set_capability_enabled(
        self, id: PairingId, category: str, name: str, *, enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable a capability of a pairing on this device.

        Only affects whether the feature is usable on the host, not the remote device.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_capability_enabled,
            None,
            {"id": id, "category": category, "name": name, "enabled": enabled},
            request_options,
        )

    async def get_plugins(self, *, request_options: RequestOptions | None = None) -> Plugins:
        """Get the plugin information. Access: admin."""
        return await self._run(OPS.get_plugins, None, {}, request_options)

    async def get_siren_light_supported(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether the siren/light plugin is supported on this device.

        Check this before using the siren/light plugin operations.

        Access: admin.
        """
        return await self._run(OPS.get_siren_light_supported, None, {}, request_options)

    async def get_siren_light(self, *, request_options: RequestOptions | None = None) -> SirenLight:
        """Get the siren/light plugin information. Access: admin."""
        return await self._run(OPS.get_siren_light, None, {}, request_options)

    async def list_siren_light_capabilities(
        self, *, request_options: RequestOptions | None = None
    ) -> list[SirenLightCapability]:
        """List the siren/light capabilities of the paired devices. Access: admin."""
        return await self._run(OPS.list_siren_light_capabilities, None, {}, request_options)

    async def get_siren_light_capability(
        self, pairing: PairingId, *, request_options: RequestOptions | None = None
    ) -> SirenLightCapability:
        """Get the siren/light capabilities of one paired device. Access: admin."""
        return await self._run(OPS.get_siren_light_capability, None, {"pairing": pairing}, request_options)

    async def list_siren_light_profiles(
        self, *, request_options: RequestOptions | None = None
    ) -> list[SirenLightProfile]:
        """List the siren/light profiles of the paired devices. Access: admin."""
        return await self._run(OPS.list_siren_light_profiles, None, {}, request_options)

    async def get_siren_light_profile(
        self, pairing: PairingId, *, request_options: RequestOptions | None = None
    ) -> SirenLightProfile:
        """List the profiles that can be started or stopped on one paired device. Access: admin."""
        return await self._run(OPS.get_siren_light_profile, None, {"pairing": pairing}, request_options)
