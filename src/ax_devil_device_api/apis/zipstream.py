# GENERATED from specs/apis/network-video/zipstream.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure Axis Zipstream bit rate reduction (strength, GOP mode, FPS mode, minimum FPS, profiles) through the XML CGIs.

Docs: https://developer.axis.com/vapix/network-video/zipstream-technology/
"""

from __future__ import annotations

from typing import Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Xml
from .._protocols.xmlmap import XmlField, XmlMap
from ..rtsp import RtspBinding, RtspUrl
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

Strength = Literal["off", "10", "20", "30", "40", "50", "60", "70", "80", "90", "100"]
GopMode = Literal["fixed", "dynamic"]
FpsMode = Literal["fixed", "dynamic"]
Profile = Literal["classic", "storage", "networkloadbalancing"]


class Status(Model):
    """Zipstream settings of one video channel."""

    channel: str = Field(validation_alias="Channel", serialization_alias="Channel")
    """The video channel number or name."""
    strength: Strength = Field(validation_alias="Strength", serialization_alias="Strength")
    gop_mode: GopMode = Field(validation_alias="GopMode", serialization_alias="GopMode")
    max_gop_length: int = Field(validation_alias="MaxGopLength", serialization_alias="MaxGopLength")
    """Maximum GOP length for Zipstream."""
    fps_mode: FpsMode | None = Field(default=None, validation_alias="FpsMode", serialization_alias="FpsMode")
    min_fps: int | None = Field(default=None, validation_alias="MinFps", serialization_alias="MinFps", ge=0)
    """The minimum dynamic frame rate; 0 lets the frame rate go as low as the dynamic frame rate can."""
    profile: str | None = Field(default=None, validation_alias="Profile", serialization_alias="Profile")
    """The Zipstream profile. Named in the prose only; not in the XSD or any example."""
    profile_level: int | None = Field(default=None, validation_alias="ProfileLevel", serialization_alias="ProfileLevel")
    """The Zipstream profile level. Named in the prose only; not in the XSD or any example."""


class Statuses(Model):
    channels: list[Status] = Field(validation_alias="Status", serialization_alias="Status")


class Strengths(Model):
    strengths: list[str] = Field(validation_alias="Strength", serialization_alias="Strength")


class GopModes(Model):
    gop_modes: list[str] = Field(validation_alias="GopMode", serialization_alias="GopMode")


class FpsModes(Model):
    fps_modes: list[str] = Field(validation_alias="FpsMode", serialization_alias="FpsMode")


class ProfileInfo(Model):
    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """The profile name."""
    max_level: int | None = Field(default=None, validation_alias="MaxLevel", serialization_alias="MaxLevel", ge=0)
    """The maximum feature level of the profile."""


class Profiles(Model):
    profiles: list[ProfileInfo] = Field(validation_alias="Profile", serialization_alias="Profile")


class SchemaVersion(Model):
    version_number: str = Field(validation_alias="VersionNumber", serialization_alias="VersionNumber")
    """Schema version, major.minor."""
    deprecated: bool | None = Field(default=None, validation_alias="Deprecated", serialization_alias="Deprecated")
    """If true, this version of the XML schema is deprecated and should not be used. Defaults to false."""


class SchemaVersions(Model):
    schema_version: list[SchemaVersion] = Field(validation_alias="SchemaVersion", serialization_alias="SchemaVersion")


class SetStrengthRequest(Model):
    schemaversion: int = Field(ge=1)
    """The major version of the XML schema to use for the response (latest supported minor version is used)."""
    camera: str | None = None
    """The video channel (1,... or channel name). If omitted, the strength is set on all channels."""
    strength: Strength
    """The Zipstream strength to set."""


class SetGopRequest(Model):
    schemaversion: int = Field(ge=1)
    """The major version of the XML schema to use for the response (latest supported minor version is used)."""
    camera: str | None = None
    """The video channel (1,... or channel name). If omitted, the GOP settings are set on all channels."""
    gopmode: GopMode | None = None
    """If omitted, the current value is used."""
    maxgoplength: int | None = Field(default=None, ge=1, le=1023)
    """Zipstream maximum GOP length. If omitted, the current value is used."""


class GetStatusRequest(Model):
    schemaversion: int = Field(ge=1)
    """The major version of the XML schema to use for the response (latest supported minor version is used)."""
    camera: str | None = None
    """The video channel (1,... or channel name). If omitted, settings for all channels are returned."""


class ListStrengthsRequest(Model):
    schemaversion: int = Field(ge=1)
    """The major version of the XML schema to use for the response (latest supported minor version is used)."""


class ListGopModesRequest(Model):
    schemaversion: int = Field(ge=1)
    """The major version of the XML schema to use for the response (latest supported minor version is used)."""


class SetFpsModeRequest(Model):
    schemaversion: int = Field(ge=1)
    """The major version of the XML schema to use for the response (latest supported minor version is used)."""
    camera: str | None = None
    """The video channel name. If omitted, all channels are set."""
    fpsmode: FpsMode
    """The FPS mode to set."""


class ListFpsModesRequest(Model):
    schemaversion: int | None = Field(default=None, ge=1)
    """The major version of the XML schema to use for the response. The syntax shows no arguments but the example passes schemaversion=1."""


class SetMinFpsRequest(Model):
    schemaversion: int = Field(ge=1)
    """The major version of the XML schema to use for the response (latest supported minor version is used)."""
    camera: str | None = None
    """The video channel (1,... or channel name). If omitted, applies to all channels."""
    minfps: int = Field(ge=0)
    """0 lets the frame rate go as low as the dynamic frame rate can; a larger value keeps the dynamic frame rate from going below it."""


class SetProfileRequest(Model):
    schemaversion: int = Field(ge=1)
    """The major version of the XML schema to use for the response (latest supported minor version is used)."""
    camera: str | None = None
    """The video channel (1,... or channel name). If omitted, the profile is set on all channels."""
    profile: Profile | None = None
    """The profile to use. The device default is classic."""
    gradualdecoderefresh: Literal["auto", "low", "balanced", "extreme"] | None = None
    """Only for the networkloadbalancing profile (default auto). auto: handled internally by the video framework. low: no forced intra blocks, but I-frames are more compressed than in other profiles. balanced: most refreshes use forced intra blocks and some I-frames are more compressed than usual. extreme: all refreshes use forced intra blocks and the initial I-frame is more compressed."""
    level: int | None = Field(default=None, ge=0)
    """The level of features; 0 (the device default) is replaced with the highest available level. The maximum level of a profile comes from list_profiles."""


class ListProfilesRequest(Model):
    schemaversion: int = Field(ge=1)
    """The major version of the XML schema to use for the response (latest supported minor version is used)."""


class GetRtspStreamWithZipstreamRequest(Model):
    videocodec: str | None = None
    """Video codec of the stream, for example h264."""
    videozstrength: Strength | None = None
    videozgopmode: GopMode | None = None
    videozmaxgoplength: int | None = Field(default=None, ge=1)
    """The maximum GOP length for dynamic GOP mode."""
    videokeyframeinterval: int | None = Field(default=None, ge=1)
    """Overrides the default GOP length (Image.I#.MPEG.PCount); the minimum GOP length in dynamic mode."""
    videozfpsmode: FpsMode | None = None
    videozminfps: int | None = Field(default=None, ge=0)
    """The minimum dynamic frame rate; only with ``videozfpsmode=dynamic``."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/zipstream/getschemaversions.cgi"

INFO = ApiInfo(
    id="zipstream",
    name="Zipstream technology",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.ZipStream.ZipStream", "yes"),),
    docs=(
        "https://developer.axis.com/vapix/network-video/zipstream-technology/",
        "http://www.axis.com/vapix/http_cgi/zipstream1.xsd",
    ),
    errors={
        10: ErrorCode("Error while processing the request."),
        40: ErrorCode("Specified version is not supported.", "unsupported"),
    },
)


class OPS:
    get_schema_versions = Operation(
        INFO,
        "get_schema_versions",
        CgiBinding(
            PATH,
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
                    root="Success/GetSchemaVersionsSuccess",
                )
            ),
        ),
        result=SchemaVersions,
        access="operator",
        effect="read",
    )
    set_strength = Operation(
        INFO,
        "set_strength",
        CgiBinding(
            "/axis-cgi/zipstream/setstrength.cgi",
            args=(CgiArg("schemaversion"), CgiArg("camera"), CgiArg("strength")),
            reply=Xml(),
        ),
        params=SetStrengthRequest,
        access="operator",
        effect="write",
        write="patch",
        errors={
            20: ErrorCode("Invalid channel.", "invalid_argument"),
            50: ErrorCode("Invalid Zipstream strength", "invalid_argument"),
        },
    )
    set_gop = Operation(
        INFO,
        "set_gop",
        CgiBinding(
            "/axis-cgi/zipstream/setgop.cgi",
            args=(CgiArg("schemaversion"), CgiArg("camera"), CgiArg("gopmode"), CgiArg("maxgoplength")),
            reply=Xml(),
        ),
        params=SetGopRequest,
        access="operator",
        effect="write",
        write="patch",
        errors={
            20: ErrorCode("Invalid channel.", "invalid_argument"),
            60: ErrorCode("Invalid GOP mode.", "invalid_argument"),
            70: ErrorCode("Invalid maximum GOP length.", "invalid_argument"),
        },
    )
    get_status = Operation(
        INFO,
        "get_status",
        CgiBinding(
            "/axis-cgi/zipstream/getstatus.cgi",
            args=(CgiArg("schemaversion"), CgiArg("camera")),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "Status",
                            source="path",
                            many=True,
                            nested=XmlMap(
                                fields=(
                                    XmlField("Channel", source="child"),
                                    XmlField("Strength", source="child"),
                                    XmlField("GopMode", source="child"),
                                    XmlField("MaxGopLength", source="child"),
                                    XmlField("FpsMode", source="child"),
                                    XmlField("MinFps", source="child"),
                                    XmlField("Profile", source="child"),
                                    XmlField("ProfileLevel", source="child"),
                                )
                            ),
                        ),
                    ),
                    root="Success/GetStatusSuccess",
                )
            ),
        ),
        params=GetStatusRequest,
        result=Statuses,
        access="operator",
        effect="read",
        errors={20: ErrorCode("Invalid channel.", "invalid_argument")},
    )
    list_strengths = Operation(
        INFO,
        "list_strengths",
        CgiBinding(
            "/axis-cgi/zipstream/liststrengths.cgi",
            args=(CgiArg("schemaversion"),),
            reply=Xml(
                map=XmlMap(
                    fields=(XmlField("Strength", source="path", many=True),), root="Success/ListStrengthsSuccess"
                )
            ),
        ),
        params=ListStrengthsRequest,
        result=Strengths,
        access="operator",
        effect="read",
    )
    list_gop_modes = Operation(
        INFO,
        "list_gop_modes",
        CgiBinding(
            "/axis-cgi/zipstream/listgopmodes.cgi",
            args=(CgiArg("schemaversion"),),
            reply=Xml(
                map=XmlMap(fields=(XmlField("GopMode", source="path", many=True),), root="Success/ListGopModesSuccess")
            ),
        ),
        params=ListGopModesRequest,
        result=GopModes,
        access="operator",
        effect="read",
    )
    set_fps_mode = Operation(
        INFO,
        "set_fps_mode",
        CgiBinding(
            "/axis-cgi/zipstream/setfpsmode.cgi",
            args=(CgiArg("schemaversion"), CgiArg("camera"), CgiArg("fpsmode")),
            reply=Xml(),
        ),
        params=SetFpsModeRequest,
        access="operator",
        effect="write",
        write="patch",
        errors={80: ErrorCode("Invalid FPS mode.", "invalid_argument")},
    )
    list_fps_modes = Operation(
        INFO,
        "list_fps_modes",
        CgiBinding(
            "/axis-cgi/zipstream/listfpsmodes.cgi",
            args=(CgiArg("schemaversion"),),
            reply=Xml(
                map=XmlMap(fields=(XmlField("FpsMode", source="path", many=True),), root="Success/ListFpsModesSuccess")
            ),
        ),
        params=ListFpsModesRequest,
        result=FpsModes,
        access="operator",
        effect="read",
    )
    set_min_fps = Operation(
        INFO,
        "set_min_fps",
        CgiBinding(
            "/axis-cgi/zipstream/setminfps.cgi",
            args=(CgiArg("schemaversion"), CgiArg("camera"), CgiArg("minfps")),
            reply=Xml(),
        ),
        params=SetMinFpsRequest,
        access="operator",
        effect="write",
        write="patch",
        errors={90: ErrorCode("Invalid minimum FPS.", "invalid_argument")},
    )
    set_profile = Operation(
        INFO,
        "set_profile",
        CgiBinding(
            "/axis-cgi/zipstream/setprofile.cgi",
            args=(
                CgiArg("schemaversion"),
                CgiArg("camera"),
                CgiArg("profile"),
                CgiArg("gradualdecoderefresh"),
                CgiArg("level"),
            ),
            reply=Xml(),
        ),
        params=SetProfileRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    list_profiles = Operation(
        INFO,
        "list_profiles",
        CgiBinding(
            "/axis-cgi/zipstream/listprofiles.cgi",
            args=(CgiArg("schemaversion"),),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "Profile",
                            source="path",
                            many=True,
                            nested=XmlMap(
                                fields=(XmlField("Name", source="child"), XmlField("MaxLevel", source="child"))
                            ),
                        ),
                    ),
                    root="Success/ListProfilesSuccess",
                )
            ),
        ),
        params=ListProfilesRequest,
        result=Profiles,
        access="operator",
        effect="read",
    )
    get_rtsp_stream_with_zipstream = Operation(
        INFO,
        "get_rtsp_stream_with_zipstream",
        RtspBinding(),
        params=GetRtspStreamWithZipstreamRequest,
        access="operator",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class ZipstreamApi(SyncApi):
    """Zipstream technology (``zipstream``)."""

    INFO = INFO

    def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """Retrieve the supported XML schema versions. Access: operator."""
        return self._run(OPS.get_schema_versions, None, {}, request_options)

    def set_strength(
        self,
        *,
        schemaversion: int,
        camera: str | MISSING = MISSING,
        strength: Strength,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the Zipstream strength on all or one video channel.

        Changes only the fields given. Access: operator.
        """
        self._run(
            OPS.set_strength,
            None,
            {"schemaversion": schemaversion, "camera": camera, "strength": strength},
            request_options,
        )

    def set_gop(
        self,
        *,
        schemaversion: int,
        camera: str | MISSING = MISSING,
        gopmode: GopMode | MISSING = MISSING,
        maxgoplength: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the GOP mode and maximum GOP length on all or one video channel.

        Changes only the fields given. Access: operator.
        """
        self._run(
            OPS.set_gop,
            None,
            {"schemaversion": schemaversion, "camera": camera, "gopmode": gopmode, "maxgoplength": maxgoplength},
            request_options,
        )

    def get_status(
        self, *, schemaversion: int, camera: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> Statuses:
        """Retrieve the current Zipstream settings (strength, GOP, FPS, profile) per channel.

        Access: operator.
        """
        return self._run(OPS.get_status, None, {"schemaversion": schemaversion, "camera": camera}, request_options)

    def list_strengths(self, *, schemaversion: int, request_options: RequestOptions | None = None) -> Strengths:
        """Retrieve the available Zipstream strengths. Access: operator."""
        return self._run(OPS.list_strengths, None, {"schemaversion": schemaversion}, request_options)

    def list_gop_modes(self, *, schemaversion: int, request_options: RequestOptions | None = None) -> GopModes:
        """List the available Zipstream GOP modes. Access: operator."""
        return self._run(OPS.list_gop_modes, None, {"schemaversion": schemaversion}, request_options)

    def set_fps_mode(
        self,
        *,
        schemaversion: int,
        camera: str | MISSING = MISSING,
        fpsmode: FpsMode,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the Zipstream FPS mode (AXIS OS 6.30 and later).

        Changes only the fields given. Access: operator.
        """
        self._run(
            OPS.set_fps_mode,
            None,
            {"schemaversion": schemaversion, "camera": camera, "fpsmode": fpsmode},
            request_options,
        )

    def list_fps_modes(
        self, *, schemaversion: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> FpsModes:
        """List the available Zipstream FPS modes. Access: operator."""
        return self._run(OPS.list_fps_modes, None, {"schemaversion": schemaversion}, request_options)

    def set_min_fps(
        self,
        *,
        schemaversion: int,
        camera: str | MISSING = MISSING,
        minfps: int,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the minimum dynamic frame rate (only relevant if FPS mode is dynamic and Zipstream is on).

        Changes only the fields given. Access: operator.
        """
        self._run(
            OPS.set_min_fps, None, {"schemaversion": schemaversion, "camera": camera, "minfps": minfps}, request_options
        )

    @overload
    def set_profile(self, request: SetProfileRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def set_profile(
        self,
        /,
        *,
        schemaversion: int,
        camera: str | MISSING = MISSING,
        profile: Profile | MISSING = MISSING,
        gradualdecoderefresh: Literal["auto", "low", "balanced", "extreme"] | MISSING = MISSING,
        level: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_profile(
        self,
        request: SetProfileRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the Zipstream profile on all or one channel.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_profile, request, kwargs, request_options)

    def list_profiles(self, *, schemaversion: int, request_options: RequestOptions | None = None) -> Profiles:
        """List all available Zipstream profiles with their maximum level. Access: operator."""
        return self._run(OPS.list_profiles, None, {"schemaversion": schemaversion}, request_options)

    def get_rtsp_stream_with_zipstream(
        self,
        *,
        videocodec: str | MISSING = MISSING,
        videozstrength: Strength | MISSING = MISSING,
        videozgopmode: GopMode | MISSING = MISSING,
        videozmaxgoplength: int | MISSING = MISSING,
        videokeyframeinterval: int | MISSING = MISSING,
        videozfpsmode: FpsMode | MISSING = MISSING,
        videozminfps: int | MISSING = MISSING,
        port: int | None = None,
        include_credentials: bool = False,
    ) -> RtspUrl:
        """Build the RTSP URL of a stream with Zipstream settings that apply to that stream only.

        The settings override the device-wide Zipstream settings (``set_strength``, ``set_gop``,
        ``set_fps_mode``, ``set_min_fps``) for the requested stream. ``videozminfps`` is only relevant when
        ``videozfpsmode`` is ``dynamic``.

        Builds the URL only; no request is made. Access: operator.
        """
        return self._device.rtsp_url_for(
            OPS.get_rtsp_stream_with_zipstream,
            {
                "videocodec": videocodec,
                "videozstrength": videozstrength,
                "videozgopmode": videozgopmode,
                "videozmaxgoplength": videozmaxgoplength,
                "videokeyframeinterval": videokeyframeinterval,
                "videozfpsmode": videozfpsmode,
                "videozminfps": videozminfps,
            },
            port=port,
            include_credentials=include_credentials,
        )


class AsyncZipstreamApi(AsyncApi):
    """Zipstream technology (``zipstream``)."""

    INFO = INFO

    async def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """Retrieve the supported XML schema versions. Access: operator."""
        return await self._run(OPS.get_schema_versions, None, {}, request_options)

    async def set_strength(
        self,
        *,
        schemaversion: int,
        camera: str | MISSING = MISSING,
        strength: Strength,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the Zipstream strength on all or one video channel.

        Changes only the fields given. Access: operator.
        """
        await self._run(
            OPS.set_strength,
            None,
            {"schemaversion": schemaversion, "camera": camera, "strength": strength},
            request_options,
        )

    async def set_gop(
        self,
        *,
        schemaversion: int,
        camera: str | MISSING = MISSING,
        gopmode: GopMode | MISSING = MISSING,
        maxgoplength: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the GOP mode and maximum GOP length on all or one video channel.

        Changes only the fields given. Access: operator.
        """
        await self._run(
            OPS.set_gop,
            None,
            {"schemaversion": schemaversion, "camera": camera, "gopmode": gopmode, "maxgoplength": maxgoplength},
            request_options,
        )

    async def get_status(
        self, *, schemaversion: int, camera: str | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> Statuses:
        """Retrieve the current Zipstream settings (strength, GOP, FPS, profile) per channel.

        Access: operator.
        """
        return await self._run(
            OPS.get_status, None, {"schemaversion": schemaversion, "camera": camera}, request_options
        )

    async def list_strengths(self, *, schemaversion: int, request_options: RequestOptions | None = None) -> Strengths:
        """Retrieve the available Zipstream strengths. Access: operator."""
        return await self._run(OPS.list_strengths, None, {"schemaversion": schemaversion}, request_options)

    async def list_gop_modes(self, *, schemaversion: int, request_options: RequestOptions | None = None) -> GopModes:
        """List the available Zipstream GOP modes. Access: operator."""
        return await self._run(OPS.list_gop_modes, None, {"schemaversion": schemaversion}, request_options)

    async def set_fps_mode(
        self,
        *,
        schemaversion: int,
        camera: str | MISSING = MISSING,
        fpsmode: FpsMode,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the Zipstream FPS mode (AXIS OS 6.30 and later).

        Changes only the fields given. Access: operator.
        """
        await self._run(
            OPS.set_fps_mode,
            None,
            {"schemaversion": schemaversion, "camera": camera, "fpsmode": fpsmode},
            request_options,
        )

    async def list_fps_modes(
        self, *, schemaversion: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> FpsModes:
        """List the available Zipstream FPS modes. Access: operator."""
        return await self._run(OPS.list_fps_modes, None, {"schemaversion": schemaversion}, request_options)

    async def set_min_fps(
        self,
        *,
        schemaversion: int,
        camera: str | MISSING = MISSING,
        minfps: int,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the minimum dynamic frame rate (only relevant if FPS mode is dynamic and Zipstream is on).

        Changes only the fields given. Access: operator.
        """
        await self._run(
            OPS.set_min_fps, None, {"schemaversion": schemaversion, "camera": camera, "minfps": minfps}, request_options
        )

    @overload
    async def set_profile(
        self, request: SetProfileRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_profile(
        self,
        /,
        *,
        schemaversion: int,
        camera: str | MISSING = MISSING,
        profile: Profile | MISSING = MISSING,
        gradualdecoderefresh: Literal["auto", "low", "balanced", "extreme"] | MISSING = MISSING,
        level: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_profile(
        self,
        request: SetProfileRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the Zipstream profile on all or one channel.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_profile, request, kwargs, request_options)

    async def list_profiles(self, *, schemaversion: int, request_options: RequestOptions | None = None) -> Profiles:
        """List all available Zipstream profiles with their maximum level. Access: operator."""
        return await self._run(OPS.list_profiles, None, {"schemaversion": schemaversion}, request_options)

    def get_rtsp_stream_with_zipstream(
        self,
        *,
        videocodec: str | MISSING = MISSING,
        videozstrength: Strength | MISSING = MISSING,
        videozgopmode: GopMode | MISSING = MISSING,
        videozmaxgoplength: int | MISSING = MISSING,
        videokeyframeinterval: int | MISSING = MISSING,
        videozfpsmode: FpsMode | MISSING = MISSING,
        videozminfps: int | MISSING = MISSING,
        port: int | None = None,
        include_credentials: bool = False,
    ) -> RtspUrl:
        """Build the RTSP URL of a stream with Zipstream settings that apply to that stream only.

        The settings override the device-wide Zipstream settings (``set_strength``, ``set_gop``,
        ``set_fps_mode``, ``set_min_fps``) for the requested stream. ``videozminfps`` is only relevant when
        ``videozfpsmode`` is ``dynamic``.

        Builds the URL only; no request is made. Access: operator.
        """
        return self._device.rtsp_url_for(
            OPS.get_rtsp_stream_with_zipstream,
            {
                "videocodec": videocodec,
                "videozstrength": videozstrength,
                "videozgopmode": videozgopmode,
                "videozmaxgoplength": videozmaxgoplength,
                "videokeyframeinterval": videokeyframeinterval,
                "videozfpsmode": videozfpsmode,
                "videozminfps": videozminfps,
            },
            port=port,
            include_credentials=include_credentials,
        )
