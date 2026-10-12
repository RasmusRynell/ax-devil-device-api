# GENERATED from specs/apis/network-video/serial-port.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Read and write raw serial data, connect video sources to ports, and configure serial ports through param.cgi.

Docs: https://developer.axis.com/vapix/network-video/serial-port-api/
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Annotated

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


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/com/serial.cgi"

INFO = ApiInfo(
    id="serial-port",
    name="Serial port API",
    family=Family.CGI,
    discovery=(
        ApiDiscovery("serial-port"),
        ParamDiscovery("Properties.API.HTTP.Version", "3"),
        ParamDiscovery("Properties.Serial.Serial", "yes"),
    ),
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
