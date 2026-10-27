# GENERATED from specs/apis/device-configuration/coordinate-conversion-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""List the coordinate spaces the device knows about and convert points from one coordinate space to another.

Docs: https://developer.axis.com/vapix/device-configuration/coordinate-conversion-api/
"""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

CoordinateSpaceAndSystem = str
Point = Annotated[list[float], Field(max_length=12)]
PointList = Annotated[list[Point], Field(max_length=1000)]
OutputPointList = list[PointList]


class Space(Model):
    """A coordinate space the device knows about."""

    name: str
    """The name of this coordinate space, for example ``cameraImage@1``."""


class CoordinateConversion(Model):
    """The whole API tree."""

    spaces: list[Space] | None = None


class ConvertRequest(Model):
    """Arguments of ``convert``."""

    name: str
    """The source coordinate space."""
    destination: CoordinateSpaceAndSystem
    points: PointList


class ConvertResponse(Model):
    """Result of ``convert``."""

    points: OutputPointList


class SpaceNameRequest(Model):
    name: str
    """The name of this coordinate space."""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/coordinate-conversion/v1"

INFO = ApiInfo(
    id="coordinate-conversion-config",
    name="Coordinate conversion API",
    family=Family.DCA,
    discovery=(DcaDiscovery("coordinate-conversion", "v1"),),
    docs=("https://developer.axis.com/vapix/device-configuration/coordinate-conversion-api/",),
)


class OPS:
    get_all = Operation(
        INFO, "get_all", DcaBinding("GET", ROOT), result=CoordinateConversion, access="viewer", effect="read"
    )
    list_spaces = Operation(
        INFO, "list_spaces", DcaBinding("GET", f"{ROOT}/spaces"), result=list[Space], access="viewer", effect="read"
    )
    get_space = Operation(
        INFO,
        "get_space",
        DcaBinding("GET", f"{ROOT}/spaces/{{name}}"),
        params=SpaceNameRequest,
        result=Space,
        access="viewer",
        effect="read",
    )
    convert = Operation(
        INFO,
        "convert",
        DcaBinding("POST", f"{ROOT}/spaces/{{name}}/convert", body="object"),
        params=ConvertRequest,
        result=ConvertResponse,
        access="viewer",
        effect="action",
    )


# ---------------------------------------------------------------------------
# API classes


class CoordinateConversionApi(SyncApi):
    """Coordinate conversion API (``coordinate-conversion-config``, v1)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> CoordinateConversion:
        """The whole API tree. Access: viewer."""
        return self._run(OPS.get_all, None, {}, request_options)

    def list_spaces(self, *, request_options: RequestOptions | None = None) -> list[Space]:
        """List the coordinate spaces the device knows about. Access: viewer."""
        return self._run(OPS.list_spaces, None, {}, request_options)

    def get_space(self, name: str, *, request_options: RequestOptions | None = None) -> Space:
        """Get one coordinate space. Access: viewer."""
        return self._run(OPS.get_space, None, {"name": name}, request_options)

    def convert(
        self,
        name: str,
        *,
        destination: CoordinateSpaceAndSystem,
        points: PointList,
        request_options: RequestOptions | None = None,
    ) -> ConvertResponse:
        """Convert points from a source coordinate space to another coordinate system.

        Points that cannot be converted come back as an empty list at the same position.

        Access: viewer.
        """
        return self._run(
            OPS.convert, None, {"name": name, "destination": destination, "points": points}, request_options
        )


class AsyncCoordinateConversionApi(AsyncApi):
    """Coordinate conversion API (``coordinate-conversion-config``, v1)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> CoordinateConversion:
        """The whole API tree. Access: viewer."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def list_spaces(self, *, request_options: RequestOptions | None = None) -> list[Space]:
        """List the coordinate spaces the device knows about. Access: viewer."""
        return await self._run(OPS.list_spaces, None, {}, request_options)

    async def get_space(self, name: str, *, request_options: RequestOptions | None = None) -> Space:
        """Get one coordinate space. Access: viewer."""
        return await self._run(OPS.get_space, None, {"name": name}, request_options)

    async def convert(
        self,
        name: str,
        *,
        destination: CoordinateSpaceAndSystem,
        points: PointList,
        request_options: RequestOptions | None = None,
    ) -> ConvertResponse:
        """Convert points from a source coordinate space to another coordinate system.

        Points that cannot be converted come back as an empty list at the same position.

        Access: viewer.
        """
        return await self._run(
            OPS.convert, None, {"name": name, "destination": destination, "points": points}, request_options
        )
