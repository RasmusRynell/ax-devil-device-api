# GENERATED from specs/apis/network-video/serial-port.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Read and write raw serial data, connect video sources to ports, and configure serial ports through param.cgi.

Docs: https://developer.axis.com/vapix/network-video/serial-port-api/
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Annotated, Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Text, TextOk
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

VideoChannel = Annotated[int, Field(ge=1)]


class WriteDataRequest(Model):
    write: str = Field(pattern="^[0-9A-Fa-f]+$")
    """The bytes to write, hexadecimal coded, for example ``2153435253500c0d``."""
    camera: VideoChannel | None = None


class WriteStringRequest(Model):
    writestring: str
    """The text to write. The client percent-encodes it in the request."""
    camera: VideoChannel | None = None


class ReadDataRequest(Model):
    read: int = Field(ge=1)
    """The number of bytes to read."""
    wait: int | None = Field(default=None, ge=1, le=9)
    """The longest time to wait for the bytes, in seconds."""
    timeout: int | None = Field(default=None, ge=0, le=9000)
    """The longest time to wait for the bytes, in milliseconds."""
    camera: VideoChannel | None = None


class ConnectVideoSourceRequest(Model):
    port: int = Field(ge=-1)
    """The port to open, or -1 to disconnect the video source."""
    camera: VideoChannel


class UpdateSerialParametersRequest(Model):
    parameters: dict[str, str]


class SetSerialPortRequest(Model):
    serial: int = Field(ge=0)
    """Serial port index n of Serial.Ser<n>; starts at 1."""
    port_mode: Literal["RS232", "RS485", "RS485_4", "RS422"] | None = Field(
        default=None, validation_alias="Serial.Ser{serial}.PortMode", serialization_alias="Serial.Ser{serial}.PortMode"
    )
    """Serial port protocol (product dependent; may be read-only depending on hardware)."""
    baud_rate: (
        Literal["300", "600", "1200", "2400", "4800", "9600", "19200", "38400", "57600", "115200", "230400", "460800"]
        | None
    ) = Field(
        default=None, validation_alias="Serial.Ser{serial}.BaudRate", serialization_alias="Serial.Ser{serial}.BaudRate"
    )
    """Transmission speed in bits per second. 230400 and 460800 only apply to RS485 and RS485_4."""
    data_bits: Literal["7", "8"] | None = Field(
        default=None, validation_alias="Serial.Ser{serial}.DataBits", serialization_alias="Serial.Ser{serial}.DataBits"
    )
    """Number of data bits."""
    stop_bits: Literal["1", "2"] | None = Field(
        default=None, validation_alias="Serial.Ser{serial}.StopBits", serialization_alias="Serial.Ser{serial}.StopBits"
    )
    """Number of stop bits."""
    parity: Literal["None", "Even", "Odd", "Mark", "Space"] | None = Field(
        default=None, validation_alias="Serial.Ser{serial}.Parity", serialization_alias="Serial.Ser{serial}.Parity"
    )
    """Parity; None adds no parity bit."""
    flow_control_xon_xoff: Literal["yes", "no"] | None = Field(
        default=None,
        validation_alias="Serial.Ser{serial}.FlowControlXONXOFF",
        serialization_alias="Serial.Ser{serial}.FlowControlXONXOFF",
    )
    """XON/XOFF flow control (needs a full duplex port); unsupported if the parameter is missing on the device."""
    flow_control_rts_cts: Literal["yes", "no"] | None = Field(
        default=None,
        validation_alias="Serial.Ser{serial}.FlowControlRTSCTS",
        serialization_alias="Serial.Ser{serial}.FlowControlRTSCTS",
    )
    """RTS/CTS flow control (needs a RS232 port); unsupported if the parameter is missing on the device."""
    termination: Literal["yes", "no"] | None = Field(
        default=None,
        validation_alias="Serial.Ser{serial}.Termination",
        serialization_alias="Serial.Ser{serial}.Termination",
    )
    """RS485/RS422 termination; unsupported if the parameter is missing on the device."""
    bias: Literal["yes", "no"] | None = Field(
        default=None, validation_alias="Serial.Ser{serial}.Bias", serialization_alias="Serial.Ser{serial}.Bias"
    )
    """RS485/RS422 bias; unsupported if the parameter is missing on the device."""


class SetPortManagerRequest(Model):
    port_manager: int = Field(ge=0)
    """Port manager index n of PortManager.P<n>; goes from 0 to the number of port managers minus 1."""
    port_enabled: Literal["yes", "no"] | None = Field(
        default=None,
        validation_alias="PortManager.P{port_manager}.PortEnabled",
        serialization_alias="PortManager.P{port_manager}.PortEnabled",
    )
    """Enable or disable the output port defined by PortType."""
    port_type: Literal["Serial", "RemotePort"] | None = Field(
        default=None,
        validation_alias="PortManager.P{port_manager}.PortType",
        serialization_alias="PortManager.P{port_manager}.PortType",
    )
    """What the port manager manages: Serial (a local serial port) or RemotePort (data forwarded to a serial port on another CPU)."""
    serial_cgi_enabled: Literal["yes", "no"] | None = Field(
        default=None,
        validation_alias="PortManager.P{port_manager}.SerialCGI.Enabled",
        serialization_alias="PortManager.P{port_manager}.SerialCGI.Enabled",
    )
    """Enable the internal server that /axis-cgi/com/serial.cgi uses to reach the port manager (default no)."""
    ptz_server_enabled: Literal["yes", "no"] | None = Field(
        default=None,
        validation_alias="PortManager.P{port_manager}.PTZServer.Enabled",
        serialization_alias="PortManager.P{port_manager}.PTZServer.Enabled",
    )
    """Enable the internal server that PTZ drivers use to reach the port manager (default no)."""
    remote_port_server_enabled: Literal["yes", "no"] | None = Field(
        default=None,
        validation_alias="PortManager.P{port_manager}.RemotePortServer.Enabled",
        serialization_alias="PortManager.P{port_manager}.RemotePortServer.Enabled",
    )
    """Enable the remote port server (default no)."""
    remote_port_server_allowed_ip_addresses: str | None = Field(
        default=None,
        validation_alias="PortManager.P{port_manager}.RemotePortServer.AllowedIPAddresses",
        serialization_alias="PortManager.P{port_manager}.RemotePortServer.AllowedIPAddresses",
    )
    """Comma separated list of IP addresses allowed to connect; ranges such as 2.3.4.5-9 and 3.4.5.* are allowed. Empty allows all."""
    remote_port_server_timeout: int | None = Field(
        default=None,
        validation_alias="PortManager.P{port_manager}.RemotePortServer.Timeout",
        serialization_alias="PortManager.P{port_manager}.RemotePortServer.Timeout",
        ge=0,
        le=3600,
    )
    """Seconds of inactivity after which a connection is closed; 0 waits forever."""
    remote_port_server_authentication_key: str | None = Field(
        default=None,
        validation_alias="PortManager.P{port_manager}.RemotePortServer.AuthenticationKey",
        serialization_alias="PortManager.P{port_manager}.RemotePortServer.AuthenticationKey",
    )
    """Key that remote port clients use when connecting to this remote port server."""
    remote_port_server_listener_enabled: Literal["yes", "no"] | None = Field(
        default=None,
        validation_alias="PortManager.P{port_manager}.RemotePortServer.Listener.Enabled",
        serialization_alias="PortManager.P{port_manager}.RemotePortServer.Listener.Enabled",
    )
    """Accept connections to the remote port server (default no)."""
    remote_port_server_listener_port: int | None = Field(
        default=None,
        validation_alias="PortManager.P{port_manager}.RemotePortServer.Listener.Port",
        serialization_alias="PortManager.P{port_manager}.RemotePortServer.Listener.Port",
        ge=1024,
        le=65535,
    )
    """Port to listen on for remote port clients (default 1024 + the port manager index)."""
    generic_tcp_server_enabled: Literal["yes", "no"] | None = Field(
        default=None,
        validation_alias="PortManager.P{port_manager}.GenericTCPServer.Enabled",
        serialization_alias="PortManager.P{port_manager}.GenericTCPServer.Enabled",
    )
    """Enable the generic TCP server (default no)."""
    generic_tcp_server_allowed_ip_addresses: str | None = Field(
        default=None,
        validation_alias="PortManager.P{port_manager}.GenericTCPServer.AllowedIPAddresses",
        serialization_alias="PortManager.P{port_manager}.GenericTCPServer.AllowedIPAddresses",
    )
    """Comma separated list of IP addresses allowed to connect; ranges such as 2.3.4.5-9 and 3.4.5.* are allowed. Empty allows all."""
    generic_tcp_server_timeout: int | None = Field(
        default=None,
        validation_alias="PortManager.P{port_manager}.GenericTCPServer.Timeout",
        serialization_alias="PortManager.P{port_manager}.GenericTCPServer.Timeout",
        ge=0,
        le=3600,
    )
    """Seconds of inactivity after which a connection is closed; 0 waits forever."""
    generic_tcp_server_connect_to_enabled: Literal["yes", "no"] | None = Field(
        default=None,
        validation_alias="PortManager.P{port_manager}.GenericTCPServer.ConnectTo.Enabled",
        serialization_alias="PortManager.P{port_manager}.GenericTCPServer.ConnectTo.Enabled",
    )
    """Let the port manager act as a client and connect to another host (default no)."""
    generic_tcp_server_connect_to_host: str | None = Field(
        default=None,
        validation_alias="PortManager.P{port_manager}.GenericTCPServer.ConnectTo.Host",
        serialization_alias="PortManager.P{port_manager}.GenericTCPServer.ConnectTo.Host",
    )
    """Host name or IP address to connect to."""
    generic_tcp_server_connect_to_port: int | None = Field(
        default=None,
        validation_alias="PortManager.P{port_manager}.GenericTCPServer.ConnectTo.Port",
        serialization_alias="PortManager.P{port_manager}.GenericTCPServer.ConnectTo.Port",
        ge=1024,
        le=65535,
    )
    """TCP port to connect to (default 1024 + the port manager index)."""
    generic_tcp_server_listener_enabled: Literal["yes", "no"] | None = Field(
        default=None,
        validation_alias="PortManager.P{port_manager}.GenericTCPServer.Listener.Enabled",
        serialization_alias="PortManager.P{port_manager}.GenericTCPServer.Listener.Enabled",
    )
    """Enable connections to the generic TCP server (default no)."""
    generic_tcp_server_listener_port: int | None = Field(
        default=None,
        validation_alias="PortManager.P{port_manager}.GenericTCPServer.Listener.Port",
        serialization_alias="PortManager.P{port_manager}.GenericTCPServer.Listener.Port",
        ge=1024,
        le=65535,
    )
    """TCP port to listen on (default 1024 + the port manager index)."""


class SetRemotePortRequest(Model):
    remote_port: int = Field(ge=0)
    """Remote port client index n of RemotePort.R<n>; starts at 0."""
    auto_conf: Literal["yes", "no"] | None = Field(
        default=None,
        validation_alias="RemotePort.R{remote_port}.AutoConf",
        serialization_alias="RemotePort.R{remote_port}.AutoConf",
    )
    """Find the address and port of the remote port server automatically using Bonjour (default yes)."""
    authentication_key: str | None = Field(
        default=None,
        validation_alias="RemotePort.R{remote_port}.AuthenticationKey",
        serialization_alias="RemotePort.R{remote_port}.AuthenticationKey",
    )
    """Key for authenticating to the remote port server (the server shows it in PortManager.P<n>.RemotePortServer.AuthenticationKey)."""
    host: str | None = Field(
        default=None,
        validation_alias="RemotePort.R{remote_port}.Host",
        serialization_alias="RemotePort.R{remote_port}.Host",
    )
    """Host name or IP address of the remote port server; ignored if AutoConf is yes."""
    port: int | None = Field(
        default=None,
        validation_alias="RemotePort.R{remote_port}.Port",
        serialization_alias="RemotePort.R{remote_port}.Port",
        ge=1024,
        le=65535,
    )
    """Listen port of the remote port server (default 5555); ignored if AutoConf is yes."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/com/serial.cgi"

INFO = ApiInfo(
    id="serial-port",
    name="Serial port API",
    family=Family.CGI,
    discovery=(ApiDiscovery("serial-port"), ParamDiscovery("Properties.Serial.Serial", "yes")),
    docs=("https://developer.axis.com/vapix/network-video/serial-port-api/",),
)


class OPS:
    write_data = Operation(
        INFO,
        "write_data",
        CgiBinding(PATH, args=(CgiArg("write"), CgiArg("camera")), reply=Text()),
        params=WriteDataRequest,
        access="viewer",
        effect="action",
    )
    write_string = Operation(
        INFO,
        "write_string",
        CgiBinding(PATH, args=(CgiArg("writestring"), CgiArg("camera")), reply=Text()),
        params=WriteStringRequest,
        access="viewer",
        effect="action",
    )
    read_data = Operation(
        INFO,
        "read_data",
        CgiBinding(PATH, args=(CgiArg("read"), CgiArg("wait"), CgiArg("timeout"), CgiArg("camera")), reply=Text()),
        params=ReadDataRequest,
        result=str,
        access="viewer",
        effect="action",
    )
    connect_video_source = Operation(
        INFO,
        "connect_video_source",
        CgiBinding(PATH, args=(CgiArg("port"), CgiArg("camera")), reply=Text()),
        params=ConnectVideoSourceRequest,
        access="viewer",
        effect="action",
    )
    update_serial_parameters = Operation(
        INFO,
        "update_serial_parameters",
        CgiBinding(
            "/axis-cgi/param.cgi",
            fixed_query=(("action", "update"),),
            args=(CgiArg("parameters", style="spread"),),
            reply=TextOk(),
        ),
        params=UpdateSerialParametersRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_serial_port = Operation(
        INFO,
        "set_serial_port",
        CgiBinding(
            "/axis-cgi/param.cgi",
            fixed_query=(("action", "update"),),
            args=(
                CgiArg("port_mode", wire="Serial.Ser{serial}.PortMode"),
                CgiArg("baud_rate", wire="Serial.Ser{serial}.BaudRate"),
                CgiArg("data_bits", wire="Serial.Ser{serial}.DataBits"),
                CgiArg("stop_bits", wire="Serial.Ser{serial}.StopBits"),
                CgiArg("parity", wire="Serial.Ser{serial}.Parity"),
                CgiArg("flow_control_xon_xoff", wire="Serial.Ser{serial}.FlowControlXONXOFF"),
                CgiArg("flow_control_rts_cts", wire="Serial.Ser{serial}.FlowControlRTSCTS"),
                CgiArg("termination", wire="Serial.Ser{serial}.Termination"),
                CgiArg("bias", wire="Serial.Ser{serial}.Bias"),
            ),
            reply=TextOk(),
        ),
        params=SetSerialPortRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_port_manager = Operation(
        INFO,
        "set_port_manager",
        CgiBinding(
            "/axis-cgi/param.cgi",
            fixed_query=(("action", "update"),),
            args=(
                CgiArg("port_enabled", wire="PortManager.P{port_manager}.PortEnabled"),
                CgiArg("port_type", wire="PortManager.P{port_manager}.PortType"),
                CgiArg("serial_cgi_enabled", wire="PortManager.P{port_manager}.SerialCGI.Enabled"),
                CgiArg("ptz_server_enabled", wire="PortManager.P{port_manager}.PTZServer.Enabled"),
                CgiArg("remote_port_server_enabled", wire="PortManager.P{port_manager}.RemotePortServer.Enabled"),
                CgiArg(
                    "remote_port_server_allowed_ip_addresses",
                    wire="PortManager.P{port_manager}.RemotePortServer.AllowedIPAddresses",
                ),
                CgiArg("remote_port_server_timeout", wire="PortManager.P{port_manager}.RemotePortServer.Timeout"),
                CgiArg(
                    "remote_port_server_authentication_key",
                    wire="PortManager.P{port_manager}.RemotePortServer.AuthenticationKey",
                ),
                CgiArg(
                    "remote_port_server_listener_enabled",
                    wire="PortManager.P{port_manager}.RemotePortServer.Listener.Enabled",
                ),
                CgiArg(
                    "remote_port_server_listener_port",
                    wire="PortManager.P{port_manager}.RemotePortServer.Listener.Port",
                ),
                CgiArg("generic_tcp_server_enabled", wire="PortManager.P{port_manager}.GenericTCPServer.Enabled"),
                CgiArg(
                    "generic_tcp_server_allowed_ip_addresses",
                    wire="PortManager.P{port_manager}.GenericTCPServer.AllowedIPAddresses",
                ),
                CgiArg("generic_tcp_server_timeout", wire="PortManager.P{port_manager}.GenericTCPServer.Timeout"),
                CgiArg(
                    "generic_tcp_server_connect_to_enabled",
                    wire="PortManager.P{port_manager}.GenericTCPServer.ConnectTo.Enabled",
                ),
                CgiArg(
                    "generic_tcp_server_connect_to_host",
                    wire="PortManager.P{port_manager}.GenericTCPServer.ConnectTo.Host",
                ),
                CgiArg(
                    "generic_tcp_server_connect_to_port",
                    wire="PortManager.P{port_manager}.GenericTCPServer.ConnectTo.Port",
                ),
                CgiArg(
                    "generic_tcp_server_listener_enabled",
                    wire="PortManager.P{port_manager}.GenericTCPServer.Listener.Enabled",
                ),
                CgiArg(
                    "generic_tcp_server_listener_port",
                    wire="PortManager.P{port_manager}.GenericTCPServer.Listener.Port",
                ),
            ),
            reply=TextOk(),
        ),
        params=SetPortManagerRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_remote_port = Operation(
        INFO,
        "set_remote_port",
        CgiBinding(
            "/axis-cgi/param.cgi",
            fixed_query=(("action", "update"),),
            args=(
                CgiArg("auto_conf", wire="RemotePort.R{remote_port}.AutoConf"),
                CgiArg("authentication_key", wire="RemotePort.R{remote_port}.AuthenticationKey"),
                CgiArg("host", wire="RemotePort.R{remote_port}.Host"),
                CgiArg("port", wire="RemotePort.R{remote_port}.Port"),
            ),
            reply=TextOk(),
        ),
        params=SetRemotePortRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class SerialPortApi(SyncApi):
    """Serial port API (``serial-port``)."""

    INFO = INFO

    def write_data(
        self, write: str, *, camera: VideoChannel | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Write hexadecimal coded bytes to the serial port. Access: viewer."""
        self._run(OPS.write_data, None, {"write": write, "camera": camera}, request_options)

    def write_string(
        self,
        writestring: str,
        *,
        camera: VideoChannel | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Write a string to the serial port. Access: viewer."""
        self._run(OPS.write_string, None, {"writestring": writestring, "camera": camera}, request_options)

    def read_data(
        self,
        read: int,
        *,
        wait: int | MISSING = MISSING,
        timeout: int | MISSING = MISSING,
        camera: VideoChannel | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Read bytes from the serial port.

        Returns the bytes hexadecimal coded and placed between ``#`` characters, for example ``#3A#``. The
        read ends when the requested number of bytes has been read, ``wait`` seconds have passed or
        ``timeout`` milliseconds have passed.

        Access: viewer.
        """
        return self._run(
            OPS.read_data, None, {"read": read, "wait": wait, "timeout": timeout, "camera": camera}, request_options
        )

    def connect_video_source(
        self, *, port: int, camera: VideoChannel, request_options: RequestOptions | None = None
    ) -> None:
        """Open a port and connect a video source to it, or disconnect the video source from any port.

        Port 2 corresponds to the port manager PortManager.P0 in the docs example; -1 disconnects the video
        source.

        Access: viewer.
        """
        self._run(OPS.connect_video_source, None, {"port": port, "camera": camera}, request_options)

    def update_serial_parameters(
        self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> None:
        """Change serial port, port manager, remote port and generic TCP parameters, e.g. ``{"Serial.Ser1.BaudRate": "9600"}``.

        The keys are parameters of the groups Serial.Ser#, PortManager.P#, RemotePort.R# and
        PortManager.P#.GenericTCPServer. Only the given parameters change.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.update_serial_parameters, None, {"parameters": dict(parameters)}, request_options)

    @overload
    def set_serial_port(
        self, request: SetSerialPortRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_serial_port(
        self,
        serial: int,
        /,
        *,
        port_mode: Literal["RS232", "RS485", "RS485_4", "RS422"] | MISSING = MISSING,
        baud_rate: Literal[
            "300", "600", "1200", "2400", "4800", "9600", "19200", "38400", "57600", "115200", "230400", "460800"
        ]
        | MISSING = MISSING,
        data_bits: Literal["7", "8"] | MISSING = MISSING,
        stop_bits: Literal["1", "2"] | MISSING = MISSING,
        parity: Literal["None", "Even", "Odd", "Mark", "Space"] | MISSING = MISSING,
        flow_control_xon_xoff: Literal["yes", "no"] | MISSING = MISSING,
        flow_control_rts_cts: Literal["yes", "no"] | MISSING = MISSING,
        termination: Literal["yes", "no"] | MISSING = MISSING,
        bias: Literal["yes", "no"] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_serial_port(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Change the settings of a serial port.

        Sets parameters of the group Serial.Ser<n>. Only the given parameters change. Which values are valid
        is product dependent.

        Changes only the fields given. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetSerialPortRequest):
            kwargs = {**dict(zip(("serial",), (request, *args), strict=False)), **kwargs}
            request = None
        self._run(OPS.set_serial_port, request, kwargs, request_options)

    @overload
    def set_port_manager(
        self, request: SetPortManagerRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_port_manager(
        self,
        port_manager: int,
        /,
        *,
        port_enabled: Literal["yes", "no"] | MISSING = MISSING,
        port_type: Literal["Serial", "RemotePort"] | MISSING = MISSING,
        serial_cgi_enabled: Literal["yes", "no"] | MISSING = MISSING,
        ptz_server_enabled: Literal["yes", "no"] | MISSING = MISSING,
        remote_port_server_enabled: Literal["yes", "no"] | MISSING = MISSING,
        remote_port_server_allowed_ip_addresses: str | MISSING = MISSING,
        remote_port_server_timeout: int | MISSING = MISSING,
        remote_port_server_authentication_key: str | MISSING = MISSING,
        remote_port_server_listener_enabled: Literal["yes", "no"] | MISSING = MISSING,
        remote_port_server_listener_port: int | MISSING = MISSING,
        generic_tcp_server_enabled: Literal["yes", "no"] | MISSING = MISSING,
        generic_tcp_server_allowed_ip_addresses: str | MISSING = MISSING,
        generic_tcp_server_timeout: int | MISSING = MISSING,
        generic_tcp_server_connect_to_enabled: Literal["yes", "no"] | MISSING = MISSING,
        generic_tcp_server_connect_to_host: str | MISSING = MISSING,
        generic_tcp_server_connect_to_port: int | MISSING = MISSING,
        generic_tcp_server_listener_enabled: Literal["yes", "no"] | MISSING = MISSING,
        generic_tcp_server_listener_port: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_port_manager(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Change the settings of a port manager.

        Sets parameters of the group PortManager.P<n> and its sub-groups (SerialCGI, PTZServer,
        RemotePortServer, GenericTCPServer). Only the given parameters change. The RemotePortServer and
        PTZServer groups do not exist on products without that functionality.

        Changes only the fields given. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetPortManagerRequest):
            kwargs = {**dict(zip(("port_manager",), (request, *args), strict=False)), **kwargs}
            request = None
        self._run(OPS.set_port_manager, request, kwargs, request_options)

    @overload
    def set_remote_port(
        self, request: SetRemotePortRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_remote_port(
        self,
        remote_port: int,
        /,
        *,
        auto_conf: Literal["yes", "no"] | MISSING = MISSING,
        authentication_key: str | MISSING = MISSING,
        host: str | MISSING = MISSING,
        port: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_remote_port(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Change the settings of a remote port client.

        Sets parameters of the group RemotePort.R<n>. The group does not exist on products without remote
        port support.

        Changes only the fields given. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetRemotePortRequest):
            kwargs = {**dict(zip(("remote_port",), (request, *args), strict=False)), **kwargs}
            request = None
        self._run(OPS.set_remote_port, request, kwargs, request_options)


class AsyncSerialPortApi(AsyncApi):
    """Serial port API (``serial-port``)."""

    INFO = INFO

    async def write_data(
        self, write: str, *, camera: VideoChannel | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Write hexadecimal coded bytes to the serial port. Access: viewer."""
        await self._run(OPS.write_data, None, {"write": write, "camera": camera}, request_options)

    async def write_string(
        self,
        writestring: str,
        *,
        camera: VideoChannel | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Write a string to the serial port. Access: viewer."""
        await self._run(OPS.write_string, None, {"writestring": writestring, "camera": camera}, request_options)

    async def read_data(
        self,
        read: int,
        *,
        wait: int | MISSING = MISSING,
        timeout: int | MISSING = MISSING,
        camera: VideoChannel | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Read bytes from the serial port.

        Returns the bytes hexadecimal coded and placed between ``#`` characters, for example ``#3A#``. The
        read ends when the requested number of bytes has been read, ``wait`` seconds have passed or
        ``timeout`` milliseconds have passed.

        Access: viewer.
        """
        return await self._run(
            OPS.read_data, None, {"read": read, "wait": wait, "timeout": timeout, "camera": camera}, request_options
        )

    async def connect_video_source(
        self, *, port: int, camera: VideoChannel, request_options: RequestOptions | None = None
    ) -> None:
        """Open a port and connect a video source to it, or disconnect the video source from any port.

        Port 2 corresponds to the port manager PortManager.P0 in the docs example; -1 disconnects the video
        source.

        Access: viewer.
        """
        await self._run(OPS.connect_video_source, None, {"port": port, "camera": camera}, request_options)

    async def update_serial_parameters(
        self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> None:
        """Change serial port, port manager, remote port and generic TCP parameters, e.g. ``{"Serial.Ser1.BaudRate": "9600"}``.

        The keys are parameters of the groups Serial.Ser#, PortManager.P#, RemotePort.R# and
        PortManager.P#.GenericTCPServer. Only the given parameters change.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.update_serial_parameters, None, {"parameters": dict(parameters)}, request_options)

    @overload
    async def set_serial_port(
        self, request: SetSerialPortRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_serial_port(
        self,
        serial: int,
        /,
        *,
        port_mode: Literal["RS232", "RS485", "RS485_4", "RS422"] | MISSING = MISSING,
        baud_rate: Literal[
            "300", "600", "1200", "2400", "4800", "9600", "19200", "38400", "57600", "115200", "230400", "460800"
        ]
        | MISSING = MISSING,
        data_bits: Literal["7", "8"] | MISSING = MISSING,
        stop_bits: Literal["1", "2"] | MISSING = MISSING,
        parity: Literal["None", "Even", "Odd", "Mark", "Space"] | MISSING = MISSING,
        flow_control_xon_xoff: Literal["yes", "no"] | MISSING = MISSING,
        flow_control_rts_cts: Literal["yes", "no"] | MISSING = MISSING,
        termination: Literal["yes", "no"] | MISSING = MISSING,
        bias: Literal["yes", "no"] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_serial_port(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Change the settings of a serial port.

        Sets parameters of the group Serial.Ser<n>. Only the given parameters change. Which values are valid
        is product dependent.

        Changes only the fields given. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetSerialPortRequest):
            kwargs = {**dict(zip(("serial",), (request, *args), strict=False)), **kwargs}
            request = None
        await self._run(OPS.set_serial_port, request, kwargs, request_options)

    @overload
    async def set_port_manager(
        self, request: SetPortManagerRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_port_manager(
        self,
        port_manager: int,
        /,
        *,
        port_enabled: Literal["yes", "no"] | MISSING = MISSING,
        port_type: Literal["Serial", "RemotePort"] | MISSING = MISSING,
        serial_cgi_enabled: Literal["yes", "no"] | MISSING = MISSING,
        ptz_server_enabled: Literal["yes", "no"] | MISSING = MISSING,
        remote_port_server_enabled: Literal["yes", "no"] | MISSING = MISSING,
        remote_port_server_allowed_ip_addresses: str | MISSING = MISSING,
        remote_port_server_timeout: int | MISSING = MISSING,
        remote_port_server_authentication_key: str | MISSING = MISSING,
        remote_port_server_listener_enabled: Literal["yes", "no"] | MISSING = MISSING,
        remote_port_server_listener_port: int | MISSING = MISSING,
        generic_tcp_server_enabled: Literal["yes", "no"] | MISSING = MISSING,
        generic_tcp_server_allowed_ip_addresses: str | MISSING = MISSING,
        generic_tcp_server_timeout: int | MISSING = MISSING,
        generic_tcp_server_connect_to_enabled: Literal["yes", "no"] | MISSING = MISSING,
        generic_tcp_server_connect_to_host: str | MISSING = MISSING,
        generic_tcp_server_connect_to_port: int | MISSING = MISSING,
        generic_tcp_server_listener_enabled: Literal["yes", "no"] | MISSING = MISSING,
        generic_tcp_server_listener_port: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_port_manager(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Change the settings of a port manager.

        Sets parameters of the group PortManager.P<n> and its sub-groups (SerialCGI, PTZServer,
        RemotePortServer, GenericTCPServer). Only the given parameters change. The RemotePortServer and
        PTZServer groups do not exist on products without that functionality.

        Changes only the fields given. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetPortManagerRequest):
            kwargs = {**dict(zip(("port_manager",), (request, *args), strict=False)), **kwargs}
            request = None
        await self._run(OPS.set_port_manager, request, kwargs, request_options)

    @overload
    async def set_remote_port(
        self, request: SetRemotePortRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_remote_port(
        self,
        remote_port: int,
        /,
        *,
        auto_conf: Literal["yes", "no"] | MISSING = MISSING,
        authentication_key: str | MISSING = MISSING,
        host: str | MISSING = MISSING,
        port: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_remote_port(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Change the settings of a remote port client.

        Sets parameters of the group RemotePort.R<n>. The group does not exist on products without remote
        port support.

        Changes only the fields given. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetRemotePortRequest):
            kwargs = {**dict(zip(("remote_port",), (request, *args), strict=False)), **kwargs}
            request = None
        await self._run(OPS.set_remote_port, request, kwargs, request_options)
