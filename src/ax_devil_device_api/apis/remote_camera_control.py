# GENERATED from specs/apis/network-video/remote-camera-control.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Manage the connection from a local camera (AXIS Q6000-E) to a remote PTZ camera: get/set connection parameters, connection status, remote URL.

Docs: https://developer.axis.com/vapix/network-video/integrating-axis-q6000-e/
"""

from __future__ import annotations

from typing import Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Xml
from .._protocols.xmlmap import XmlField, XmlMap
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

DiscoveryMode = Literal["auto", "manual"]


class BaseConnectionParams(Model):
    mac_address: str = Field(validation_alias="MACAddress", serialization_alias="MACAddress")
    """The remote camera Ethernet MAC address."""
    host: str = Field(validation_alias="Host", serialization_alias="Host")
    """The host name, IPv4 address or IPv6 address used when connecting to the remote camera."""
    discovery_mode: DiscoveryMode = Field(validation_alias="DiscoveryMode", serialization_alias="DiscoveryMode")
    """Address discovery mode: auto discovers the remote IPv4 address automatically; manual uses the configured host."""


class VapixConnectionParams(Model):
    http_port: int = Field(validation_alias="HTTPPort", serialization_alias="HTTPPort", ge=0)
    """The HTTP port used in the connection to the remote camera."""
    https_port: int = Field(validation_alias="HTTPSPort", serialization_alias="HTTPSPort", ge=0)
    """The HTTPS port used in the connection to the remote camera."""
    rtsp_port: int = Field(validation_alias="RTSPPort", serialization_alias="RTSPPort", ge=0)
    """The RTSP port used in the connection to the remote camera."""
    username: str = Field(validation_alias="Username", serialization_alias="Username")
    """User name for a user account on the remote camera."""


class VapixParams(Model):
    base_connection_params: BaseConnectionParams = Field(
        validation_alias="BaseConnectionParams", serialization_alias="BaseConnectionParams"
    )
    vapix_connection_params: VapixConnectionParams = Field(
        validation_alias="VapixConnectionParams", serialization_alias="VapixConnectionParams"
    )


class ConnectionStatus(Model):
    status_code: int = Field(validation_alias="StatusCode", serialization_alias="StatusCode", ge=0)
    """0 Connection OK, 1 Trying to connect, 2 No connection, 3 Not authorized."""
    description: str = Field(validation_alias="Description", serialization_alias="Description")
    """Status description."""


class VapixConnectionStatus(Model):
    http_status: ConnectionStatus = Field(validation_alias="HTTPStatus", serialization_alias="HTTPStatus")
    """HTTP connection status."""
    https_status: ConnectionStatus = Field(validation_alias="HTTPSStatus", serialization_alias="HTTPSStatus")
    """HTTPS connection status."""
    rtsp_status: ConnectionStatus = Field(validation_alias="RTSPStatus", serialization_alias="RTSPStatus")
    """RTSP connection status."""


class VapixStatus(Model):
    base_connection_status: ConnectionStatus = Field(
        validation_alias="BaseConnectionStatus", serialization_alias="BaseConnectionStatus"
    )
    """Base connection status."""
    vapix_connection_status: VapixConnectionStatus = Field(
        validation_alias="VapixConnectionStatus", serialization_alias="VapixConnectionStatus"
    )


class RemoteUrl(Model):
    url: str = Field(validation_alias="Url", serialization_alias="Url")
    """The URL to the remote camera."""


class SchemaVersion(Model):
    version_number: str = Field(validation_alias="VersionNumber", serialization_alias="VersionNumber")
    """The version number of the XML schema, major.minor."""
    deprecated: bool | None = Field(default=None, validation_alias="Deprecated", serialization_alias="Deprecated")
    """If true, this version of the XML schema is deprecated and should not be used. Defaults to false."""


class SchemaVersions(Model):
    schema_version: list[SchemaVersion] = Field(validation_alias="SchemaVersion", serialization_alias="SchemaVersion")


class GetVapixParamsRequest(Model):
    schemaversion: str = Field(pattern=r"^[0-9]+(\.[0-9]+)?$")
    """The version of the XML schema to use for the response, in the form major[.minor]. The major version is required; if the minor version is omitted the latest minor version is used."""


class SetVapixParamsRequest(Model):
    schemaversion: str = Field(pattern=r"^[0-9]+(\.[0-9]+)?$")
    """The version of the XML schema to use for the response, in the form major[.minor]. The major version is required; if the minor version is omitted the latest minor version is used."""
    host: str | None = None
    """The remote camera host address: host name, IPv4 address or IPv6 address."""
    discoverymode: DiscoveryMode | None = None
    """auto: the local camera discovers the remote camera IPv4 address automatically (the default). manual: the address is not discovered and must be set using host. IPv6 requires manual mode and host."""
    httpport: int | None = Field(default=None, ge=1, le=65535)
    """The remote camera's HTTP port. Default: the current HTTP port setting."""
    httpsport: int | None = Field(default=None, ge=1, le=65535)
    """The remote camera's HTTPS port. Default: the current HTTPS port setting."""
    rtspport: int | None = Field(default=None, ge=1, le=65535)
    """The remote camera's RTSP port. Default: the current RTSP port setting."""
    username: str | None = None
    """User name for a user account on the remote camera."""
    password: str | None = None
    """Password for the user account."""


class GetVapixStatusRequest(Model):
    schemaversion: str = Field(pattern=r"^[0-9]+(\.[0-9]+)?$")
    """The version of the XML schema to use for the response, in the form major[.minor]. The major version is required; if the minor version is omitted the latest minor version is used."""


class GetRemoteUrlRequest(Model):
    schemaversion: str = Field(pattern=r"^[0-9]+(\.[0-9]+)?$")
    """The version of the XML schema to use for the response, in the form major[.minor]. The major version is required; if the minor version is omitted the latest minor version is used."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/remotecameracontrol/getvapixparams.cgi"

INFO = ApiInfo(
    id="remote-camera-control",
    name="Remote camera control API",
    family=Family.CGI,
    discovery=(
        ParamDiscovery("Properties.API.HTTP.Version", "3"),
        ParamDiscovery("Properties.RemoteCameraControl.VAPIX", "yes"),
    ),
    docs=("https://developer.axis.com/vapix/network-video/integrating-axis-q6000-e/",),
    errors={
        10: ErrorCode("Error while processing the request."),
        20: ErrorCode("Invalid request.", "invalid_argument"),
        40: ErrorCode("Specified version is not supported.", "unsupported"),
    },
)


class OPS:
    get_vapix_params = Operation(
        INFO,
        "get_vapix_params",
        CgiBinding(
            PATH,
            args=(CgiArg("schemaversion"),),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "BaseConnectionParams",
                            source="path",
                            nested=XmlMap(
                                fields=(
                                    XmlField("MACAddress", source="child"),
                                    XmlField("Host", source="child"),
                                    XmlField("DiscoveryMode", source="child"),
                                )
                            ),
                        ),
                        XmlField(
                            "VapixConnectionParams",
                            source="path",
                            nested=XmlMap(
                                fields=(
                                    XmlField("HTTPPort", source="child"),
                                    XmlField("HTTPSPort", source="child"),
                                    XmlField("RTSPPort", source="child"),
                                    XmlField("Username", source="child"),
                                )
                            ),
                        ),
                    ),
                    root="GetVapixParamsSuccess",
                )
            ),
        ),
        params=GetVapixParamsRequest,
        result=VapixParams,
        access="admin",
        effect="read",
    )
    set_vapix_params = Operation(
        INFO,
        "set_vapix_params",
        CgiBinding(
            "/axis-cgi/remotecameracontrol/setvapixparams.cgi",
            args=(
                CgiArg("schemaversion"),
                CgiArg("host"),
                CgiArg("discoverymode"),
                CgiArg("httpport"),
                CgiArg("httpsport"),
                CgiArg("rtspport"),
                CgiArg("username"),
                CgiArg("password"),
            ),
            reply=Xml(),
        ),
        params=SetVapixParamsRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_vapix_status = Operation(
        INFO,
        "get_vapix_status",
        CgiBinding(
            "/axis-cgi/remotecameracontrol/getvapixstatus.cgi",
            args=(CgiArg("schemaversion"),),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "BaseConnectionStatus",
                            source="path",
                            nested=XmlMap(
                                fields=(XmlField("StatusCode", source="child"), XmlField("Description", source="child"))
                            ),
                        ),
                        XmlField(
                            "VapixConnectionStatus",
                            source="path",
                            nested=XmlMap(
                                fields=(
                                    XmlField(
                                        "HTTPStatus",
                                        source="path",
                                        nested=XmlMap(
                                            fields=(
                                                XmlField("StatusCode", source="child"),
                                                XmlField("Description", source="child"),
                                            )
                                        ),
                                    ),
                                    XmlField(
                                        "HTTPSStatus",
                                        source="path",
                                        nested=XmlMap(
                                            fields=(
                                                XmlField("StatusCode", source="child"),
                                                XmlField("Description", source="child"),
                                            )
                                        ),
                                    ),
                                    XmlField(
                                        "RTSPStatus",
                                        source="path",
                                        nested=XmlMap(
                                            fields=(
                                                XmlField("StatusCode", source="child"),
                                                XmlField("Description", source="child"),
                                            )
                                        ),
                                    ),
                                )
                            ),
                        ),
                    ),
                    root="*",
                )
            ),
        ),
        params=GetVapixStatusRequest,
        result=VapixStatus,
        access="viewer",
        effect="read",
    )
    get_remote_url = Operation(
        INFO,
        "get_remote_url",
        CgiBinding(
            "/axis-cgi/remotecameracontrol/getremoteurl.cgi",
            args=(CgiArg("schemaversion"),),
            reply=Xml(map=XmlMap(fields=(XmlField("Url", source="text"),), root="*")),
        ),
        params=GetRemoteUrlRequest,
        result=RemoteUrl,
        access="viewer",
        effect="read",
    )
    get_schema_versions = Operation(
        INFO,
        "get_schema_versions",
        CgiBinding(
            "/axis-cgi/remotecameracontrol/schemaversions.cgi",
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "SchemaVersion",
                            source="path",
                            many=True,
                            nested=XmlMap(
                                fields=(
                                    XmlField("VersionNumber", source="child"),
                                    XmlField("Deprecated", source="child"),
                                )
                            ),
                        ),
                    ),
                    root="*",
                )
            ),
        ),
        result=SchemaVersions,
        access="viewer",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class RemoteCameraControlApi(SyncApi):
    """Remote camera control API (``remote-camera-control``)."""

    INFO = INFO

    def get_vapix_params(self, *, schemaversion: str, request_options: RequestOptions | None = None) -> VapixParams:
        """Retrieve connection parameters used for the remote camera. Access: admin."""
        return self._run(OPS.get_vapix_params, None, {"schemaversion": schemaversion}, request_options)

    @overload
    def set_vapix_params(
        self, request: SetVapixParamsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_vapix_params(
        self,
        /,
        *,
        schemaversion: str,
        host: str | MISSING = MISSING,
        discoverymode: DiscoveryMode | MISSING = MISSING,
        httpport: int | MISSING = MISSING,
        httpsport: int | MISSING = MISSING,
        rtspport: int | MISSING = MISSING,
        username: str | MISSING = MISSING,
        password: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_vapix_params(
        self,
        request: SetVapixParamsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set connection parameters (only used in the connection; remote camera settings are not changed).

        Parameters that are not given keep the remote camera's current settings.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_vapix_params, request, kwargs, request_options)

    def get_vapix_status(self, *, schemaversion: str, request_options: RequestOptions | None = None) -> VapixStatus:
        """Retrieve connection status. Access: viewer."""
        return self._run(OPS.get_vapix_status, None, {"schemaversion": schemaversion}, request_options)

    def get_remote_url(self, *, schemaversion: str, request_options: RequestOptions | None = None) -> RemoteUrl:
        """Retrieve the URL of the remote camera. Access: viewer."""
        return self._run(OPS.get_remote_url, None, {"schemaversion": schemaversion}, request_options)

    def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """List supported XML schema versions and whether they are deprecated. Access: viewer."""
        return self._run(OPS.get_schema_versions, None, {}, request_options)


class AsyncRemoteCameraControlApi(AsyncApi):
    """Remote camera control API (``remote-camera-control``)."""

    INFO = INFO

    async def get_vapix_params(
        self, *, schemaversion: str, request_options: RequestOptions | None = None
    ) -> VapixParams:
        """Retrieve connection parameters used for the remote camera. Access: admin."""
        return await self._run(OPS.get_vapix_params, None, {"schemaversion": schemaversion}, request_options)

    @overload
    async def set_vapix_params(
        self, request: SetVapixParamsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_vapix_params(
        self,
        /,
        *,
        schemaversion: str,
        host: str | MISSING = MISSING,
        discoverymode: DiscoveryMode | MISSING = MISSING,
        httpport: int | MISSING = MISSING,
        httpsport: int | MISSING = MISSING,
        rtspport: int | MISSING = MISSING,
        username: str | MISSING = MISSING,
        password: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_vapix_params(
        self,
        request: SetVapixParamsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set connection parameters (only used in the connection; remote camera settings are not changed).

        Parameters that are not given keep the remote camera's current settings.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_vapix_params, request, kwargs, request_options)

    async def get_vapix_status(
        self, *, schemaversion: str, request_options: RequestOptions | None = None
    ) -> VapixStatus:
        """Retrieve connection status. Access: viewer."""
        return await self._run(OPS.get_vapix_status, None, {"schemaversion": schemaversion}, request_options)

    async def get_remote_url(self, *, schemaversion: str, request_options: RequestOptions | None = None) -> RemoteUrl:
        """Retrieve the URL of the remote camera. Access: viewer."""
        return await self._run(OPS.get_remote_url, None, {"schemaversion": schemaversion}, request_options)

    async def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """List supported XML schema versions and whether they are deprecated. Access: viewer."""
        return await self._run(OPS.get_schema_versions, None, {}, request_options)
