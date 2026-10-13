# GENERATED from specs/apis/network-video/thermal-color-palettes.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""List the pseudocolor palettes of a thermal camera and select the global palette (``Image.I0.Appearance.Palette``).

Docs: https://developer.axis.com/vapix/network-video/thermal-imaging/
"""

from __future__ import annotations

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Stream, TextOk, Xml
from .._protocols.xmlmap import XmlField, XmlMap
from .._runtime.driver import AsyncStreamResult, StreamResult
from .._streams import Part
from ..rtsp import RtspBinding, RtspUrl
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class PaletteName(Model):
    value: str
    """The palette name, for example ``White-hot`` or ``Iso-Axis-WH``. Names starting with ``Iso`` are isotherm palettes."""


class PaletteDefinition(Model):
    """The definition of the ``Image.I0.Appearance.Palette`` parameter."""

    name: str | None = None
    """The parameter name, ``Palette``."""
    nice_name: str | None = Field(default=None, validation_alias="niceName", serialization_alias="niceName")
    value: str | None = None
    """The palette that is currently set."""
    security_level: str | None = Field(
        default=None, validation_alias="securityLevel", serialization_alias="securityLevel"
    )
    palettes: list[PaletteName]
    """The palettes the product supports."""


class SetGlobalPaletteRequest(Model):
    palette: str = Field(
        validation_alias="Image.I0.Appearance.Palette", serialization_alias="Image.I0.Appearance.Palette"
    )
    """The palette name, as listed by ``list_palettes``."""


class GetMjpegStreamWithPaletteRequest(Model):
    palette: str | None = None
    """The palette name, for example Axis."""


class GetRtspStreamWithPaletteRequest(Model):
    videocodec: str | None = None
    """Video codec of the stream, for example h264."""
    palette: str | None = None
    """The palette name, for example Axis."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/param.cgi"

INFO = ApiInfo(
    id="thermal-color-palettes",
    name="Thermal imaging color palettes",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.Image.Palette.Palette", "yes"),),
    docs=("https://developer.axis.com/vapix/network-video/thermal-imaging/",),
)


class OPS:
    list_palettes = Operation(
        INFO,
        "list_palettes",
        CgiBinding(
            PATH,
            fixed_query=(
                ("action", "listdefinitions"),
                ("listformat", "xmlschema"),
                ("group", "Image.*.Appearance.Palette"),
            ),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField("name"),
                        XmlField("niceName"),
                        XmlField("value"),
                        XmlField("securityLevel"),
                        XmlField(
                            "palettes",
                            source="path",
                            name="type/enum/entry",
                            many=True,
                            nested=XmlMap(fields=(XmlField("value"),)),
                        ),
                    ),
                    root="group/group/group/group/parameter",
                )
            ),
        ),
        result=PaletteDefinition,
        access="viewer",
        effect="read",
    )
    set_global_palette = Operation(
        INFO,
        "set_global_palette",
        CgiBinding(
            PATH,
            fixed_query=(("action", "update"),),
            args=(CgiArg("palette", wire="Image.I0.Appearance.Palette"),),
            reply=TextOk(),
        ),
        params=SetGlobalPaletteRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_mjpeg_stream_with_palette = Operation(
        INFO,
        "get_mjpeg_stream_with_palette",
        CgiBinding("/axis-cgi/mjpg/video.cgi", args=(CgiArg("palette"),), reply=Stream("mjpeg"), stream=True),
        params=GetMjpegStreamWithPaletteRequest,
        access="viewer",
        effect="read",
    )
    get_rtsp_stream_with_palette = Operation(
        INFO,
        "get_rtsp_stream_with_palette",
        RtspBinding(),
        params=GetRtspStreamWithPaletteRequest,
        access="viewer",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class ThermalColorPalettesApi(SyncApi):
    """Thermal imaging color palettes (``thermal-color-palettes``)."""

    INFO = INFO

    def list_palettes(self, *, request_options: RequestOptions | None = None) -> PaletteDefinition:
        """List the palettes the product supports and the one that is set.

        Reads the definition of ``Image.*.Appearance.Palette`` with ``param.cgi?action=listdefinitions``.
        Which palettes are available depends on the product; isotherm palettes (names starting with ``Iso``)
        are listed once isothermal imaging is enabled. Only the first matching parameter is returned.

        Access: viewer.
        """
        return self._run(OPS.list_palettes, None, {}, request_options)

    def set_global_palette(self, palette: str, *, request_options: RequestOptions | None = None) -> None:
        """Change the global palette, which is also the default for streams requested without a ``palette`` argument.

        Choose a name returned by ``list_palettes``, for example ``Axis`` or the isotherm palette ``Iso-
        Axis-WH``. Isotherm palettes need isothermal imaging enabled with the Isotherm API first.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_global_palette, None, {"palette": palette}, request_options)

    def get_mjpeg_stream_with_palette(
        self, *, palette: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> StreamResult[Part]:
        """Open a Motion JPEG stream that uses a given color palette.

        ``palette`` is a name returned by ``list_palettes``. Applicable if
        ``Properties.Image.Palette.StreamPalette`` is ``yes`` or does not exist. Without ``palette`` the
        global palette is used. Use the result as a context manager.

        The result streams the body: use it as a context manager (``with`` / ``async with``) and iterate it.
        Access: viewer.
        """
        return self._run(OPS.get_mjpeg_stream_with_palette, None, {"palette": palette}, request_options)

    def get_rtsp_stream_with_palette(
        self,
        *,
        videocodec: str | MISSING = MISSING,
        palette: str | MISSING = MISSING,
        port: int | None = None,
        include_credentials: bool = False,
    ) -> RtspUrl:
        """Build the RTSP URL of a stream that uses a given color palette.

        Builds the URL only; no request is made. Access: viewer.
        """
        return self._device.rtsp_url_for(
            OPS.get_rtsp_stream_with_palette,
            {"videocodec": videocodec, "palette": palette},
            port=port,
            include_credentials=include_credentials,
        )


class AsyncThermalColorPalettesApi(AsyncApi):
    """Thermal imaging color palettes (``thermal-color-palettes``)."""

    INFO = INFO

    async def list_palettes(self, *, request_options: RequestOptions | None = None) -> PaletteDefinition:
        """List the palettes the product supports and the one that is set.

        Reads the definition of ``Image.*.Appearance.Palette`` with ``param.cgi?action=listdefinitions``.
        Which palettes are available depends on the product; isotherm palettes (names starting with ``Iso``)
        are listed once isothermal imaging is enabled. Only the first matching parameter is returned.

        Access: viewer.
        """
        return await self._run(OPS.list_palettes, None, {}, request_options)

    async def set_global_palette(self, palette: str, *, request_options: RequestOptions | None = None) -> None:
        """Change the global palette, which is also the default for streams requested without a ``palette`` argument.

        Choose a name returned by ``list_palettes``, for example ``Axis`` or the isotherm palette ``Iso-
        Axis-WH``. Isotherm palettes need isothermal imaging enabled with the Isotherm API first.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_global_palette, None, {"palette": palette}, request_options)

    async def get_mjpeg_stream_with_palette(
        self, *, palette: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> AsyncStreamResult[Part]:
        """Open a Motion JPEG stream that uses a given color palette.

        ``palette`` is a name returned by ``list_palettes``. Applicable if
        ``Properties.Image.Palette.StreamPalette`` is ``yes`` or does not exist. Without ``palette`` the
        global palette is used. Use the result as a context manager.

        The result streams the body: use it as a context manager (``with`` / ``async with``) and iterate it.
        Access: viewer.
        """
        return await self._run(OPS.get_mjpeg_stream_with_palette, None, {"palette": palette}, request_options)

    def get_rtsp_stream_with_palette(
        self,
        *,
        videocodec: str | MISSING = MISSING,
        palette: str | MISSING = MISSING,
        port: int | None = None,
        include_credentials: bool = False,
    ) -> RtspUrl:
        """Build the RTSP URL of a stream that uses a given color palette.

        Builds the URL only; no request is made. Access: viewer.
        """
        return self._device.rtsp_url_for(
            OPS.get_rtsp_stream_with_palette,
            {"videocodec": videocodec, "palette": palette},
            port=port,
            include_credentials=include_credentials,
        )
