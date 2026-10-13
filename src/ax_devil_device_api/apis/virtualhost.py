# GENERATED from specs/apis/device-configuration/virtualhost-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Create, list, modify and remove virtual hosts, each with its own authentication scheme (basic, digest or OpenID Connect).

Docs: https://developer.axis.com/vapix/device-configuration/virtual-host/
"""

from __future__ import annotations

from typing import Annotated

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

AuthType = Annotated[str, Field(min_length=1, max_length=32, pattern="^(basic|digest|oidc)$")]
PortType = Annotated[int, Field(ge=1, le=65535)]
ServerNameType = Annotated[str, Field(min_length=1, max_length=64, pattern="^[A-Za-z0-9-.]+$")]


class VirtualhostEntry(Model):
    """A configured virtual host."""

    active: bool | None = None
    """Whether the virtual host is active."""
    auth_type: AuthType | None = None
    """The authentication scheme of the virtual host."""
    port: PortType | None = None
    """The port the virtual host uses."""
    server_name: ServerNameType
    """Server name of the virtual host."""


class Virtualhost(Model):
    """The whole API tree."""

    virtualhosts: list[VirtualhostEntry] | None = None


class CreateVirtualHostRequest(Model):
    """Arguments of ``create_virtual_host``."""

    active: bool | None = None
    """Virtual host state, active or not."""
    auth_type: AuthType | None = None
    """Authentication type."""
    port: PortType | None = None
    """Port number."""
    server_name: ServerNameType
    """Server name that the virtual host is based on."""

    @classmethod
    def from_current(cls, entry: VirtualhostEntry) -> CreateVirtualHostRequest:
        """A request that rewrites ``entry`` unchanged: copy it, edit fields, send it back."""
        data = entry.request_data()
        return cls.from_response_data(data)


class UpdateVirtualhostRequest(Model):
    """Arguments of ``update_virtualhost``."""

    server_name: ServerNameType
    active: bool | None = None
    """Whether the virtual host is active."""
    auth_type: AuthType | None = None
    """The authentication scheme of the virtual host."""
    port: PortType | None = None
    """The port the virtual host uses."""


class ServerNameRequest(Model):
    server_name: ServerNameType


class SetVirtualhostActiveRequest(Model):
    server_name: ServerNameType
    active: bool
    """Whether the virtual host is active."""


class SetVirtualhostAuthTypeRequest(Model):
    server_name: ServerNameType
    auth_type: AuthType
    """The authentication scheme of the virtual host."""


class SetVirtualhostPortRequest(Model):
    server_name: ServerNameType
    port: PortType
    """The port the virtual host uses."""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/virtualhost/v1"

INFO = ApiInfo(
    id="virtualhost-config",
    name="Virtual Host",
    family=Family.DCA,
    discovery=(DcaDiscovery("virtualhost", "v1"),),
    docs=("https://developer.axis.com/vapix/device-configuration/virtual-host/",),
)


class OPS:
    get_all = Operation(INFO, "get_all", DcaBinding("GET", ROOT), result=Virtualhost, access="admin", effect="read")
    create_virtual_host = Operation(
        INFO,
        "create_virtual_host",
        DcaBinding("POST", f"{ROOT}/create_virtualHost", body="object"),
        params=CreateVirtualHostRequest,
        access="admin",
        effect="write",
        write="create",
    )
    list_virtualhosts = Operation(
        INFO,
        "list_virtualhosts",
        DcaBinding("GET", f"{ROOT}/virtualhosts"),
        result=list[VirtualhostEntry],
        access="admin",
        effect="read",
    )
    get_virtualhost = Operation(
        INFO,
        "get_virtualhost",
        DcaBinding("GET", f"{ROOT}/virtualhosts/{{server_name}}"),
        params=ServerNameRequest,
        result=VirtualhostEntry,
        access="admin",
        effect="read",
    )
    update_virtualhost = Operation(
        INFO,
        "update_virtualhost",
        DcaBinding("PATCH", f"{ROOT}/virtualhosts/{{server_name}}", body="object"),
        params=UpdateVirtualhostRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    remove_virtualhost = Operation(
        INFO,
        "remove_virtualhost",
        DcaBinding("DELETE", f"{ROOT}/virtualhosts/{{server_name}}"),
        params=ServerNameRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    get_virtualhost_active = Operation(
        INFO,
        "get_virtualhost_active",
        DcaBinding("GET", f"{ROOT}/virtualhosts/{{server_name}}/active"),
        params=ServerNameRequest,
        result=bool,
        access="admin",
        effect="read",
    )
    set_virtualhost_active = Operation(
        INFO,
        "set_virtualhost_active",
        DcaBinding("PATCH", f"{ROOT}/virtualhosts/{{server_name}}/active", body="value", body_field="active"),
        params=SetVirtualhostActiveRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_virtualhost_auth_type = Operation(
        INFO,
        "get_virtualhost_auth_type",
        DcaBinding("GET", f"{ROOT}/virtualhosts/{{server_name}}/auth_type"),
        params=ServerNameRequest,
        result=AuthType,
        access="admin",
        effect="read",
    )
    set_virtualhost_auth_type = Operation(
        INFO,
        "set_virtualhost_auth_type",
        DcaBinding("PATCH", f"{ROOT}/virtualhosts/{{server_name}}/auth_type", body="value", body_field="auth_type"),
        params=SetVirtualhostAuthTypeRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_virtualhost_port = Operation(
        INFO,
        "get_virtualhost_port",
        DcaBinding("GET", f"{ROOT}/virtualhosts/{{server_name}}/port"),
        params=ServerNameRequest,
        result=PortType,
        access="admin",
        effect="read",
    )
    set_virtualhost_port = Operation(
        INFO,
        "set_virtualhost_port",
        DcaBinding("PATCH", f"{ROOT}/virtualhosts/{{server_name}}/port", body="value", body_field="port"),
        params=SetVirtualhostPortRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class VirtualhostApi(SyncApi):
    """Virtual Host (``virtualhost-config``, v1)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> Virtualhost:
        """All configured virtual hosts. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    def create_virtual_host(
        self,
        *,
        active: bool | MISSING = MISSING,
        auth_type: AuthType | MISSING = MISSING,
        port: PortType | MISSING = MISSING,
        server_name: ServerNameType,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Create a virtual host. Access: admin."""
        self._run(
            OPS.create_virtual_host,
            None,
            {"active": active, "auth_type": auth_type, "port": port, "server_name": server_name},
            request_options,
        )

    def list_virtualhosts(self, *, request_options: RequestOptions | None = None) -> list[VirtualhostEntry]:
        """List the virtual hosts. Access: admin."""
        return self._run(OPS.list_virtualhosts, None, {}, request_options)

    def get_virtualhost(
        self, server_name: ServerNameType, *, request_options: RequestOptions | None = None
    ) -> VirtualhostEntry:
        """Get one virtual host. Access: admin."""
        return self._run(OPS.get_virtualhost, None, {"server_name": server_name}, request_options)

    def update_virtualhost(
        self,
        server_name: ServerNameType,
        *,
        active: bool | MISSING = MISSING,
        auth_type: AuthType | MISSING = MISSING,
        port: PortType | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Change the active state, authentication type or port of a virtual host.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.update_virtualhost,
            None,
            {"server_name": server_name, "active": active, "auth_type": auth_type, "port": port},
            request_options,
        )

    def remove_virtualhost(self, server_name: ServerNameType, *, request_options: RequestOptions | None = None) -> None:
        """Remove a virtual host. Connections that used it become unreachable. Access: admin."""
        self._run(OPS.remove_virtualhost, None, {"server_name": server_name}, request_options)

    def get_virtualhost_active(
        self, server_name: ServerNameType, *, request_options: RequestOptions | None = None
    ) -> bool:
        """Whether a virtual host is active. Access: admin."""
        return self._run(OPS.get_virtualhost_active, None, {"server_name": server_name}, request_options)

    def set_virtualhost_active(
        self, server_name: ServerNameType, *, active: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Activate or deactivate a virtual host. Changes only the fields given. Access: admin."""
        self._run(OPS.set_virtualhost_active, None, {"server_name": server_name, "active": active}, request_options)

    def get_virtualhost_auth_type(
        self, server_name: ServerNameType, *, request_options: RequestOptions | None = None
    ) -> AuthType:
        """The authentication type of a virtual host. Access: admin."""
        return self._run(OPS.get_virtualhost_auth_type, None, {"server_name": server_name}, request_options)

    def set_virtualhost_auth_type(
        self, server_name: ServerNameType, *, auth_type: AuthType, request_options: RequestOptions | None = None
    ) -> None:
        """Set the authentication type of a virtual host.

        Changes only the fields given. Access: admin.
        """
        self._run(
            OPS.set_virtualhost_auth_type, None, {"server_name": server_name, "auth_type": auth_type}, request_options
        )

    def get_virtualhost_port(
        self, server_name: ServerNameType, *, request_options: RequestOptions | None = None
    ) -> PortType:
        """The port of a virtual host. Access: admin."""
        return self._run(OPS.get_virtualhost_port, None, {"server_name": server_name}, request_options)

    def set_virtualhost_port(
        self, server_name: ServerNameType, *, port: PortType, request_options: RequestOptions | None = None
    ) -> None:
        """Set the port of a virtual host. Changes only the fields given. Access: admin."""
        self._run(OPS.set_virtualhost_port, None, {"server_name": server_name, "port": port}, request_options)


class AsyncVirtualhostApi(AsyncApi):
    """Virtual Host (``virtualhost-config``, v1)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> Virtualhost:
        """All configured virtual hosts. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def create_virtual_host(
        self,
        *,
        active: bool | MISSING = MISSING,
        auth_type: AuthType | MISSING = MISSING,
        port: PortType | MISSING = MISSING,
        server_name: ServerNameType,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Create a virtual host. Access: admin."""
        await self._run(
            OPS.create_virtual_host,
            None,
            {"active": active, "auth_type": auth_type, "port": port, "server_name": server_name},
            request_options,
        )

    async def list_virtualhosts(self, *, request_options: RequestOptions | None = None) -> list[VirtualhostEntry]:
        """List the virtual hosts. Access: admin."""
        return await self._run(OPS.list_virtualhosts, None, {}, request_options)

    async def get_virtualhost(
        self, server_name: ServerNameType, *, request_options: RequestOptions | None = None
    ) -> VirtualhostEntry:
        """Get one virtual host. Access: admin."""
        return await self._run(OPS.get_virtualhost, None, {"server_name": server_name}, request_options)

    async def update_virtualhost(
        self,
        server_name: ServerNameType,
        *,
        active: bool | MISSING = MISSING,
        auth_type: AuthType | MISSING = MISSING,
        port: PortType | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Change the active state, authentication type or port of a virtual host.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.update_virtualhost,
            None,
            {"server_name": server_name, "active": active, "auth_type": auth_type, "port": port},
            request_options,
        )

    async def remove_virtualhost(
        self, server_name: ServerNameType, *, request_options: RequestOptions | None = None
    ) -> None:
        """Remove a virtual host. Connections that used it become unreachable. Access: admin."""
        await self._run(OPS.remove_virtualhost, None, {"server_name": server_name}, request_options)

    async def get_virtualhost_active(
        self, server_name: ServerNameType, *, request_options: RequestOptions | None = None
    ) -> bool:
        """Whether a virtual host is active. Access: admin."""
        return await self._run(OPS.get_virtualhost_active, None, {"server_name": server_name}, request_options)

    async def set_virtualhost_active(
        self, server_name: ServerNameType, *, active: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Activate or deactivate a virtual host. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_virtualhost_active, None, {"server_name": server_name, "active": active}, request_options
        )

    async def get_virtualhost_auth_type(
        self, server_name: ServerNameType, *, request_options: RequestOptions | None = None
    ) -> AuthType:
        """The authentication type of a virtual host. Access: admin."""
        return await self._run(OPS.get_virtualhost_auth_type, None, {"server_name": server_name}, request_options)

    async def set_virtualhost_auth_type(
        self, server_name: ServerNameType, *, auth_type: AuthType, request_options: RequestOptions | None = None
    ) -> None:
        """Set the authentication type of a virtual host.

        Changes only the fields given. Access: admin.
        """
        await self._run(
            OPS.set_virtualhost_auth_type, None, {"server_name": server_name, "auth_type": auth_type}, request_options
        )

    async def get_virtualhost_port(
        self, server_name: ServerNameType, *, request_options: RequestOptions | None = None
    ) -> PortType:
        """The port of a virtual host. Access: admin."""
        return await self._run(OPS.get_virtualhost_port, None, {"server_name": server_name}, request_options)

    async def set_virtualhost_port(
        self, server_name: ServerNameType, *, port: PortType, request_options: RequestOptions | None = None
    ) -> None:
        """Set the port of a virtual host. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_virtualhost_port, None, {"server_name": server_name, "port": port}, request_options)
