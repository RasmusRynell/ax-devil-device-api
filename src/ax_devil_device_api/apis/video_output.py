# GENERATED from specs/apis/network-video/video-output.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Display video sources on a video output (HDMI): source, sequence, quad view and PiP modes, mirroring, rotation, overlays.

Docs: https://developer.axis.com/vapix/network-video/video-output-api/
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Xml
from .._protocols.xmlmap import XmlField, XmlMap
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class SchemaVersion(Model):
    version_number: str = Field(validation_alias="VersionNumber", serialization_alias="VersionNumber")
    """Schema version."""
    deprecated: bool | None = Field(default=None, validation_alias="Deprecated", serialization_alias="Deprecated")
    """If true, this version of the XML schema is deprecated and should not be used."""


class SchemaVersions(Model):
    schema_version: list[SchemaVersion] = Field(validation_alias="SchemaVersion", serialization_alias="SchemaVersion")


class VideoSource(Model):
    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name")
    """Video source name."""
    id: str = Field(validation_alias="Id", serialization_alias="Id")
    """Video source identifier."""
    active: bool | None = Field(default=None, validation_alias="Active", serialization_alias="Active")
    """Whether the video source is used for video output."""


class VideoSources(Model):
    video_source: list[VideoSource] = Field(validation_alias="VideoSource", serialization_alias="VideoSource")


class Mirroring(Model):
    mirroring_enabled: bool = Field(validation_alias="MirroringEnabled", serialization_alias="MirroringEnabled")
    """Whether the video output is mirrored."""


class AddedSequenceElement(Model):
    sequence_element_id: int = Field(validation_alias="SequenceElementId", serialization_alias="SequenceElementId")
    """The id of the added element; use it to remove or update the element."""


class SequenceElement(Model):
    sequence_element_id: int = Field(validation_alias="SequenceElementId", serialization_alias="SequenceElementId")
    """The element id."""
    source: str | None = Field(default=None, validation_alias="Source", serialization_alias="Source")
    """The video source Id or the path to a bitmap."""
    duration: int | None = Field(default=None, validation_alias="Duration", serialization_alias="Duration")
    """Duration in seconds."""
    mirror: bool | None = Field(default=None, validation_alias="Mirror", serialization_alias="Mirror")
    """Whether the source or image is mirrored (sent as 0 or 1)."""


class Sequence(Model):
    elements: list[SequenceElement] = Field(
        validation_alias="VideoSequenceElement", serialization_alias="VideoSequenceElement"
    )


class QuadView(Model):
    sources: list[str] = Field(validation_alias="QuadViewSource", serialization_alias="QuadViewSource")
    """The video source Ids, ordered top left, top right, bottom left, bottom right."""


class Rotation(Model):
    degrees: int = Field(validation_alias="Degrees", serialization_alias="Degrees")
    """The clockwise rotation in degrees."""
    quad_view_support: bool | None = Field(
        default=None, validation_alias="QuadViewSupport", serialization_alias="QuadViewSupport"
    )
    """Whether this rotation is supported in quad view."""
    active: bool | None = Field(default=None, validation_alias="Active", serialization_alias="Active")
    """Whether this rotation is the active one."""


class Rotations(Model):
    rotation: list[Rotation] = Field(validation_alias="Rotation", serialization_alias="Rotation")


class SourceSetting(Model):
    id: str = Field(validation_alias="Id", serialization_alias="Id")
    """Video source Id."""
    enabled: bool | None = Field(default=None, validation_alias="Enabled", serialization_alias="Enabled")
    """Whether the Image-parameter settings are used on the video source."""


class SourceSettings(Model):
    source_setting: list[SourceSetting] = Field(validation_alias="SourceSetting", serialization_alias="SourceSetting")


class SupportedCgis(Model):
    """For each CGI whether the product supports it."""

    get_schema_versions: bool | None = Field(
        default=None, validation_alias="GetSchemaVersions", serialization_alias="GetSchemaVersions"
    )
    get_active_mode: bool | None = Field(
        default=None, validation_alias="GetActiveMode", serialization_alias="GetActiveMode"
    )
    set_active_mode: bool | None = Field(
        default=None, validation_alias="SetActiveMode", serialization_alias="SetActiveMode"
    )
    get_mirroring: bool | None = Field(
        default=None, validation_alias="GetMirroring", serialization_alias="GetMirroring"
    )
    set_mirroring: bool | None = Field(
        default=None, validation_alias="SetMirroring", serialization_alias="SetMirroring"
    )
    get_video_sources: bool | None = Field(
        default=None, validation_alias="GetVideoSources", serialization_alias="GetVideoSources"
    )
    set_video_sources: bool | None = Field(
        default=None, validation_alias="SetVideoSources", serialization_alias="SetVideoSources"
    )
    get_sequence: bool | None = Field(default=None, validation_alias="GetSequence", serialization_alias="GetSequence")
    add_sequence_element: bool | None = Field(
        default=None, validation_alias="AddSequenceElement", serialization_alias="AddSequenceElement"
    )
    remove_sequence_element: bool | None = Field(
        default=None, validation_alias="RemoveSequenceElement", serialization_alias="RemoveSequenceElement"
    )
    update_sequence_element: bool | None = Field(
        default=None, validation_alias="UpdateSequenceElement", serialization_alias="UpdateSequenceElement"
    )
    clear_sequence: bool | None = Field(
        default=None, validation_alias="ClearSequence", serialization_alias="ClearSequence"
    )
    get_quad_view: bool | None = Field(default=None, validation_alias="GetQuadView", serialization_alias="GetQuadView")
    set_quad_view: bool | None = Field(default=None, validation_alias="SetQuadView", serialization_alias="SetQuadView")
    get_rotation: bool | None = Field(default=None, validation_alias="GetRotation", serialization_alias="GetRotation")
    set_rotation: bool | None = Field(default=None, validation_alias="SetRotation", serialization_alias="SetRotation")
    get_source_settings_enabled: bool | None = Field(
        default=None, validation_alias="GetSourceSettingsEnabled", serialization_alias="GetSourceSettingsEnabled"
    )
    set_source_settings_enabled: bool | None = Field(
        default=None, validation_alias="SetSourceSettingsEnabled", serialization_alias="SetSourceSettingsEnabled"
    )
    set_pi_p: bool | None = Field(default=None, validation_alias="SetPiP", serialization_alias="SetPiP")
    get_pi_p: bool | None = Field(default=None, validation_alias="GetPiP", serialization_alias="GetPiP")
    set_dynamic_overlays: bool | None = Field(
        default=None, validation_alias="SetDynamicOverlays", serialization_alias="SetDynamicOverlays"
    )
    get_dynamic_overlays: bool | None = Field(
        default=None, validation_alias="GetDynamicOverlays", serialization_alias="GetDynamicOverlays"
    )


class ActiveMode(Model):
    name: str = Field(validation_alias="Name", serialization_alias="Name")
    """The mode name."""
    active: bool | None = Field(default=None, validation_alias="Active", serialization_alias="Active")
    """Whether the mode is active."""


class ActiveModes(Model):
    modes: list[ActiveMode] = Field(validation_alias="Mode", serialization_alias="Mode")


class PipOption(Model):
    """The current value of a PiP setting and the values it can take."""

    current_value: str | None = Field(default=None, validation_alias="CurrentValue", serialization_alias="CurrentValue")
    """The current value."""
    available_values: list[str] | None = Field(
        default=None, validation_alias="AvailableValues", serialization_alias="AvailableValues"
    )
    """The available values."""


class PipSwitch(Model):
    current_value: bool | None = Field(
        default=None, validation_alias="CurrentValue", serialization_alias="CurrentValue"
    )
    """The current value."""


class PipSettings(Model):
    """The PiP settings. The picture-in-picture is called SubView in the reply and pip in set_pip."""

    border_enabled: PipSwitch | None = Field(
        default=None, validation_alias="BorderEnabled", serialization_alias="BorderEnabled"
    )
    border_color: PipOption | None = Field(
        default=None, validation_alias="BorderColor", serialization_alias="BorderColor"
    )
    border_width: PipOption | None = Field(
        default=None, validation_alias="BorderWidth", serialization_alias="BorderWidth"
    )
    height: PipOption | None = Field(default=None, validation_alias="Height", serialization_alias="Height")
    main_view_mirroring: PipOption | None = Field(
        default=None, validation_alias="MainViewMirroring", serialization_alias="MainViewMirroring"
    )
    main_view_rotation: PipOption | None = Field(
        default=None, validation_alias="MainViewRotation", serialization_alias="MainViewRotation"
    )
    main_view_source: PipOption | None = Field(
        default=None, validation_alias="MainViewSource", serialization_alias="MainViewSource"
    )
    position: PipOption | None = Field(default=None, validation_alias="Position", serialization_alias="Position")
    sub_view_mirroring: PipOption | None = Field(
        default=None, validation_alias="SubViewMirroring", serialization_alias="SubViewMirroring"
    )
    sub_view_rotation: PipOption | None = Field(
        default=None, validation_alias="SubViewRotation", serialization_alias="SubViewRotation"
    )
    sub_view_source: PipOption | None = Field(
        default=None, validation_alias="SubViewSource", serialization_alias="SubViewSource"
    )
    width: PipOption | None = Field(default=None, validation_alias="Width", serialization_alias="Width")


class DynamicOverlays(Model):
    dynamic_overlays_enabled: bool = Field(
        validation_alias="DynamicOverlaysEnabled", serialization_alias="DynamicOverlaysEnabled"
    )
    """Whether dynamic overlays are enabled."""


class GetSchemaVersionsRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""


class GetVideoSourcesRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""


class SetVideoSourceRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""
    id: str
    """The video source identifier: the content of the Id element returned by get_video_sources."""


class GetMirroringRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""


class SetMirroringRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""
    mirroringenabled: bool
    """true mirrors the video output, false does not."""


class AddSequenceElementRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""
    source: str
    """The video source or image to add: the Id from get_video_sources for a video source, or the path to a bitmap (uploaded with the Overlay API)."""
    duration: int
    """Duration in seconds of the video source or image in the sequence."""
    mirror: bool | None = None
    """Whether the video source or image should be mirrored."""


class RemoveSequenceElementRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""
    sequenceelementid: int
    """The element to remove; the SequenceElementId returned by add_sequence_element and get_sequence."""


class UpdateSequenceElementRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""
    sequenceelementid: int
    """The element to update; the SequenceElementId returned by add_sequence_element and get_sequence."""
    sourceid: str | None = None
    """The video source Id from get_video_sources or a path to a bitmap."""
    duration: int | None = None
    """Duration in seconds of the video source or image in the sequence."""
    mirror: bool | None = None
    """Whether the video source or image should be mirrored."""


class GetSequenceRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""


class ClearSequenceRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""


class GetQuadViewRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""


class SetQuadViewRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""
    id: list[str] = Field(min_length=4, max_length=4)
    """The four video source Ids from get_video_sources, ordered top left, top right, bottom left, bottom right."""


class GetRotationRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""


class SetRotationRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""
    rotation: int
    """The clockwise rotation of the video output in degrees."""


class GetSourceSettingsEnabledRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""


class SetSourceSettingsEnabledRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""
    id: str
    """The video source Id from get_video_sources."""
    enabled: bool
    """Enable or disable mirroring, rotation and overlays (the Image-parameter settings) on the selected video source."""


class GetSupportedRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""


class GetActiveModeRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""


class SetActiveModeRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""
    mode: Literal["source", "sequence", "quad", "PiP"]
    """The desired mode."""


class GetPipRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""


class SetPipRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""
    bordercolor: list[Annotated[float, Field(ge=0, le=1)]] | None = Field(default=None, min_length=3, max_length=3)
    """The border color as red, green and blue, each 0 to 1.0. Red is 1.0,0,0."""
    borderenabled: bool | None = None
    """Show or hide the border of the picture-in-picture."""
    borderweight: list[Annotated[float, Field(ge=0, le=1)]] | None = Field(default=None, min_length=4, max_length=4)
    """The border weight in fractions of the picture-in-picture size: left, top, right and bottom. 0.01 for each is a border of 1 percent."""
    height: float | None = Field(default=None, ge=0, le=1)
    """Height of the picture-in-picture as a fraction of the output resolution height (0.0 < height < 1.0)."""
    mainviewmirroring: bool | None = None
    """Whether the main view should be mirrored."""
    mainviewrotation: Literal[0, 180] | None = None
    """Rotation of the main view in degrees."""
    mainviewsource: int | None = Field(default=None, ge=1)
    """The camera source shown in the main view, from 1 to the number of ports on the camera."""
    position: Literal["top_left", "top_right", "bottom_left", "bottom_right"] | None = None
    """Position of the picture-in-picture."""
    pipmirroring: bool | None = None
    """Whether the picture-in-picture should be mirrored."""
    piprotation: Literal[0, 180] | None = None
    """Rotation of the picture-in-picture in degrees."""
    pipsource: int | None = Field(default=None, ge=1)
    """The camera source shown in the picture-in-picture, from 1 to the number of ports on the camera."""
    width: float | None = Field(default=None, ge=0, le=1)
    """Width of the picture-in-picture as a fraction of the output resolution width (0.0 < width < 1.0)."""


class GetDynamicOverlaysRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""


class SetDynamicOverlaysRequest(Model):
    schemaversion: int
    """The major version of the XML schema to use for the response."""
    dynamicoverlays: bool
    """Enable or disable dynamic overlays."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/videooutput/getschemaversions.cgi"

INFO = ApiInfo(
    id="video-output",
    name="Video output API",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.VideoOutputControl.VideoOutputControl", "yes"),),
    docs=("https://developer.axis.com/vapix/network-video/video-output-api/",),
    errors={
        10: ErrorCode("Error while processing the request."),
        20: ErrorCode("Invalid value.", "invalid_argument"),
        30: ErrorCode("Invalid action."),
        40: ErrorCode("Specified version is not supported.", "unsupported"),
        50: ErrorCode("Quad view is not configured.", "unavailable"),
        60: ErrorCode("Invalid quad view rotation.", "invalid_argument"),
        70: ErrorCode("Unsupported feature.", "unsupported"),
    },
)


class OPS:
    get_schema_versions = Operation(
        INFO,
        "get_schema_versions",
        CgiBinding(
            PATH,
            args=(CgiArg("schemaversion"),),
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
        params=GetSchemaVersionsRequest,
        result=SchemaVersions,
        access="operator",
        effect="read",
    )
    get_video_sources = Operation(
        INFO,
        "get_video_sources",
        CgiBinding(
            "/axis-cgi/videooutput/getvideosources.cgi",
            args=(CgiArg("schemaversion"),),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "VideoSource",
                            source="path",
                            many=True,
                            nested=XmlMap(
                                fields=(
                                    XmlField("Name", source="child"),
                                    XmlField("Id", source="child"),
                                    XmlField("Active", source="child"),
                                )
                            ),
                        ),
                    ),
                    root="Success/GetVideoSourcesSuccess",
                )
            ),
        ),
        params=GetVideoSourcesRequest,
        result=VideoSources,
        access="operator",
        effect="read",
    )
    set_video_source = Operation(
        INFO,
        "set_video_source",
        CgiBinding(
            "/axis-cgi/videooutput/setvideosource.cgi", args=(CgiArg("schemaversion"), CgiArg("id")), reply=Xml()
        ),
        params=SetVideoSourceRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_mirroring = Operation(
        INFO,
        "get_mirroring",
        CgiBinding(
            "/axis-cgi/videooutput/getmirroring.cgi",
            args=(CgiArg("schemaversion"),),
            reply=Xml(
                map=XmlMap(fields=(XmlField("MirroringEnabled", source="child"),), root="Success/GetMirroringSuccess")
            ),
        ),
        params=GetMirroringRequest,
        result=Mirroring,
        access="operator",
        effect="read",
    )
    set_mirroring = Operation(
        INFO,
        "set_mirroring",
        CgiBinding(
            "/axis-cgi/videooutput/setmirroring.cgi",
            args=(CgiArg("schemaversion"), CgiArg("mirroringenabled")),
            reply=Xml(),
        ),
        params=SetMirroringRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    add_sequence_element = Operation(
        INFO,
        "add_sequence_element",
        CgiBinding(
            "/axis-cgi/videooutput/addsequenceelement.cgi",
            args=(CgiArg("schemaversion"), CgiArg("source"), CgiArg("duration"), CgiArg("mirror")),
            reply=Xml(
                map=XmlMap(fields=(XmlField("SequenceElementId", source="child"),), root="Success/AddSequenceSuccess")
            ),
        ),
        params=AddSequenceElementRequest,
        result=AddedSequenceElement,
        access="operator",
        effect="write",
        write="create",
    )
    remove_sequence_element = Operation(
        INFO,
        "remove_sequence_element",
        CgiBinding(
            "/axis-cgi/videooutput/removesequenceelement.cgi",
            args=(CgiArg("schemaversion"), CgiArg("sequenceelementid")),
            reply=Xml(),
        ),
        params=RemoveSequenceElementRequest,
        access="operator",
        effect="write",
        write="delete",
    )
    update_sequence_element = Operation(
        INFO,
        "update_sequence_element",
        CgiBinding(
            "/axis-cgi/videooutput/updatesequenceelement.cgi",
            args=(
                CgiArg("schemaversion"),
                CgiArg("sequenceelementid"),
                CgiArg("sourceid"),
                CgiArg("duration"),
                CgiArg("mirror"),
            ),
            reply=Xml(),
        ),
        params=UpdateSequenceElementRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_sequence = Operation(
        INFO,
        "get_sequence",
        CgiBinding(
            "/axis-cgi/videooutput/getsequence.cgi",
            args=(CgiArg("schemaversion"),),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "VideoSequenceElement",
                            source="path",
                            many=True,
                            nested=XmlMap(
                                fields=(
                                    XmlField("SequenceElementId", source="child"),
                                    XmlField("Source", source="child"),
                                    XmlField("Duration", source="child"),
                                    XmlField("Mirror", source="child"),
                                )
                            ),
                        ),
                    ),
                    root="Success/GetSequenceSuccess",
                )
            ),
        ),
        params=GetSequenceRequest,
        result=Sequence,
        access="operator",
        effect="read",
    )
    clear_sequence = Operation(
        INFO,
        "clear_sequence",
        CgiBinding("/axis-cgi/videooutput/clearsequence.cgi", args=(CgiArg("schemaversion"),), reply=Xml()),
        params=ClearSequenceRequest,
        access="operator",
        effect="write",
        write="delete",
    )
    get_quad_view = Operation(
        INFO,
        "get_quad_view",
        CgiBinding(
            "/axis-cgi/videooutput/getquadview.cgi",
            args=(CgiArg("schemaversion"),),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField("QuadViewSource", source="path", name="QuadViewSource/QuadViewSource", many=True),
                    ),
                    root="Success/GetQuadViewSuccess",
                )
            ),
        ),
        params=GetQuadViewRequest,
        result=QuadView,
        access="operator",
        effect="read",
    )
    set_quad_view = Operation(
        INFO,
        "set_quad_view",
        CgiBinding(
            "/axis-cgi/videooutput/setquadview.cgi",
            args=(CgiArg("schemaversion"), CgiArg("id", style="csv")),
            reply=Xml(),
        ),
        params=SetQuadViewRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_rotation = Operation(
        INFO,
        "get_rotation",
        CgiBinding(
            "/axis-cgi/videooutput/getrotation.cgi",
            args=(CgiArg("schemaversion"),),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "Rotation",
                            source="path",
                            many=True,
                            nested=XmlMap(
                                fields=(
                                    XmlField("Degrees", source="child"),
                                    XmlField("QuadViewSupport", source="child"),
                                    XmlField("Active", source="child"),
                                )
                            ),
                        ),
                    ),
                    root="Success/GetRotationSuccess",
                )
            ),
        ),
        params=GetRotationRequest,
        result=Rotations,
        access="operator",
        effect="read",
    )
    set_rotation = Operation(
        INFO,
        "set_rotation",
        CgiBinding(
            "/axis-cgi/videooutput/setrotation.cgi", args=(CgiArg("schemaversion"), CgiArg("rotation")), reply=Xml()
        ),
        params=SetRotationRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_source_settings_enabled = Operation(
        INFO,
        "get_source_settings_enabled",
        CgiBinding(
            "/axis-cgi/videooutput/getsourcesettingsenabled.cgi",
            args=(CgiArg("schemaversion"),),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "SourceSetting",
                            source="path",
                            many=True,
                            nested=XmlMap(fields=(XmlField("Id", source="child"), XmlField("Enabled", source="child"))),
                        ),
                    ),
                    root="Success/GetSourceSettingsEnabledSuccess",
                )
            ),
        ),
        params=GetSourceSettingsEnabledRequest,
        result=SourceSettings,
        access="operator",
        effect="read",
    )
    set_source_settings_enabled = Operation(
        INFO,
        "set_source_settings_enabled",
        CgiBinding(
            "/axis-cgi/videooutput/setsourcesettingsenabled.cgi",
            args=(CgiArg("schemaversion"), CgiArg("id"), CgiArg("enabled")),
            reply=Xml(),
        ),
        params=SetSourceSettingsEnabledRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_supported = Operation(
        INFO,
        "get_supported",
        CgiBinding(
            "/axis-cgi/videooutput/getsupported.cgi",
            args=(CgiArg("schemaversion"),),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField("GetSchemaVersions", source="child"),
                        XmlField("GetActiveMode", source="child"),
                        XmlField("SetActiveMode", source="child"),
                        XmlField("GetMirroring", source="child"),
                        XmlField("SetMirroring", source="child"),
                        XmlField("GetVideoSources", source="child"),
                        XmlField("SetVideoSources", source="child"),
                        XmlField("GetSequence", source="child"),
                        XmlField("AddSequenceElement", source="child"),
                        XmlField("RemoveSequenceElement", source="child"),
                        XmlField("UpdateSequenceElement", source="child"),
                        XmlField("ClearSequence", source="child"),
                        XmlField("GetQuadView", source="child"),
                        XmlField("SetQuadView", source="child"),
                        XmlField("GetRotation", source="child"),
                        XmlField("SetRotation", source="child"),
                        XmlField("GetSourceSettingsEnabled", source="child"),
                        XmlField("SetSourceSettingsEnabled", source="child"),
                        XmlField("SetPiP", source="child"),
                        XmlField("GetPiP", source="child"),
                        XmlField("SetDynamicOverlays", source="child"),
                        XmlField("GetDynamicOverlays", source="child"),
                    ),
                    root="Success/GetSupportedSuccess",
                )
            ),
        ),
        params=GetSupportedRequest,
        result=SupportedCgis,
        access="operator",
        effect="read",
    )
    get_active_mode = Operation(
        INFO,
        "get_active_mode",
        CgiBinding(
            "/axis-cgi/videooutput/getactivemode.cgi",
            args=(CgiArg("schemaversion"),),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "Mode",
                            source="path",
                            many=True,
                            nested=XmlMap(
                                fields=(XmlField("Name", source="child"), XmlField("Active", source="child"))
                            ),
                        ),
                    ),
                    root="Success/GetActiveModeSuccess",
                )
            ),
        ),
        params=GetActiveModeRequest,
        result=ActiveModes,
        access="operator",
        effect="read",
    )
    set_active_mode = Operation(
        INFO,
        "set_active_mode",
        CgiBinding(
            "/axis-cgi/videooutput/setactivemode.cgi", args=(CgiArg("schemaversion"), CgiArg("mode")), reply=Xml()
        ),
        params=SetActiveModeRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_pip = Operation(
        INFO,
        "get_pip",
        CgiBinding(
            "/axis-cgi/videooutput/getpip.cgi",
            args=(CgiArg("schemaversion"),),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "BorderEnabled",
                            source="path",
                            nested=XmlMap(fields=(XmlField("CurrentValue", source="child"),)),
                        ),
                        XmlField(
                            "BorderColor",
                            source="path",
                            nested=XmlMap(
                                fields=(
                                    XmlField("CurrentValue", source="child"),
                                    XmlField("AvailableValues", source="path", name="AvailableValues/Name", many=True),
                                )
                            ),
                        ),
                        XmlField(
                            "BorderWidth",
                            source="path",
                            nested=XmlMap(
                                fields=(
                                    XmlField("CurrentValue", source="child"),
                                    XmlField("AvailableValues", source="path", name="AvailableValues/Name", many=True),
                                )
                            ),
                        ),
                        XmlField(
                            "Height",
                            source="path",
                            nested=XmlMap(
                                fields=(
                                    XmlField("CurrentValue", source="child"),
                                    XmlField("AvailableValues", source="path", name="AvailableValues/Name", many=True),
                                )
                            ),
                        ),
                        XmlField(
                            "MainViewMirroring",
                            source="path",
                            nested=XmlMap(
                                fields=(
                                    XmlField("CurrentValue", source="child"),
                                    XmlField("AvailableValues", source="path", name="AvailableValues/Name", many=True),
                                )
                            ),
                        ),
                        XmlField(
                            "MainViewRotation",
                            source="path",
                            nested=XmlMap(
                                fields=(
                                    XmlField("CurrentValue", source="child"),
                                    XmlField("AvailableValues", source="path", name="AvailableValues/Name", many=True),
                                )
                            ),
                        ),
                        XmlField(
                            "MainViewSource",
                            source="path",
                            nested=XmlMap(
                                fields=(
                                    XmlField("CurrentValue", source="child"),
                                    XmlField("AvailableValues", source="path", name="AvailableValues/Name", many=True),
                                )
                            ),
                        ),
                        XmlField(
                            "Position",
                            source="path",
                            nested=XmlMap(
                                fields=(
                                    XmlField("CurrentValue", source="child"),
                                    XmlField("AvailableValues", source="path", name="AvailableValues/Name", many=True),
                                )
                            ),
                        ),
                        XmlField(
                            "SubViewMirroring",
                            source="path",
                            nested=XmlMap(
                                fields=(
                                    XmlField("CurrentValue", source="child"),
                                    XmlField("AvailableValues", source="path", name="AvailableValues/Name", many=True),
                                )
                            ),
                        ),
                        XmlField(
                            "SubViewRotation",
                            source="path",
                            nested=XmlMap(
                                fields=(
                                    XmlField("CurrentValue", source="child"),
                                    XmlField("AvailableValues", source="path", name="AvailableValues/Name", many=True),
                                )
                            ),
                        ),
                        XmlField(
                            "SubViewSource",
                            source="path",
                            nested=XmlMap(
                                fields=(
                                    XmlField("CurrentValue", source="child"),
                                    XmlField("AvailableValues", source="path", name="AvailableValues/Name", many=True),
                                )
                            ),
                        ),
                        XmlField(
                            "Width",
                            source="path",
                            nested=XmlMap(
                                fields=(
                                    XmlField("CurrentValue", source="child"),
                                    XmlField("AvailableValues", source="path", name="AvailableValues/Name", many=True),
                                )
                            ),
                        ),
                    ),
                    root="Success/GetPiPSuccess",
                )
            ),
        ),
        params=GetPipRequest,
        result=PipSettings,
        access="operator",
        effect="read",
    )
    set_pip = Operation(
        INFO,
        "set_pip",
        CgiBinding(
            "/axis-cgi/videooutput/setpip.cgi",
            args=(
                CgiArg("schemaversion"),
                CgiArg("bordercolor", style="csv"),
                CgiArg("borderenabled"),
                CgiArg("borderweight", style="csv"),
                CgiArg("height"),
                CgiArg("mainviewmirroring"),
                CgiArg("mainviewrotation"),
                CgiArg("mainviewsource"),
                CgiArg("position"),
                CgiArg("pipmirroring"),
                CgiArg("piprotation"),
                CgiArg("pipsource"),
                CgiArg("width"),
            ),
            reply=Xml(),
        ),
        params=SetPipRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    get_dynamic_overlays = Operation(
        INFO,
        "get_dynamic_overlays",
        CgiBinding(
            "/axis-cgi/videooutput/getdynamicoverlays.cgi",
            args=(CgiArg("schemaversion"),),
            reply=Xml(
                map=XmlMap(
                    fields=(XmlField("DynamicOverlaysEnabled", source="child"),),
                    root="Success/GetDynamicOverlaySuccess",
                )
            ),
        ),
        params=GetDynamicOverlaysRequest,
        result=DynamicOverlays,
        access="operator",
        effect="read",
    )
    set_dynamic_overlays = Operation(
        INFO,
        "set_dynamic_overlays",
        CgiBinding(
            "/axis-cgi/videooutput/setdynamicoverlays.cgi",
            args=(CgiArg("schemaversion"), CgiArg("dynamicoverlays")),
            reply=Xml(),
        ),
        params=SetDynamicOverlaysRequest,
        access="operator",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class VideoOutputApi(SyncApi):
    """Video output API (``video-output``)."""

    INFO = INFO

    def get_schema_versions(
        self, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> SchemaVersions:
        """Retrieve the supported XML schema versions. Access: operator."""
        return self._run(OPS.get_schema_versions, None, {"schemaversion": schemaversion}, request_options)

    def get_video_sources(self, *, schemaversion: int, request_options: RequestOptions | None = None) -> VideoSources:
        """Retrieve available video sources; sources used as video output are marked active.

        Access: operator.
        """
        return self._run(OPS.get_video_sources, None, {"schemaversion": schemaversion}, request_options)

    def set_video_source(self, id: str, *, schemaversion: int, request_options: RequestOptions | None = None) -> None:
        """Set the video source to display as video output.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_video_source, None, {"schemaversion": schemaversion, "id": id}, request_options)

    def get_mirroring(self, *, schemaversion: int, request_options: RequestOptions | None = None) -> Mirroring:
        """Check if the video output is mirrored. Access: operator."""
        return self._run(OPS.get_mirroring, None, {"schemaversion": schemaversion}, request_options)

    def set_mirroring(
        self, mirroringenabled: bool, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> None:
        """Mirror the video output (recordings and other streams are not affected).

        Changes only the fields given. Access: operator.
        """
        self._run(
            OPS.set_mirroring,
            None,
            {"schemaversion": schemaversion, "mirroringenabled": mirroringenabled},
            request_options,
        )

    def add_sequence_element(
        self,
        *,
        schemaversion: int,
        source: str,
        duration: int,
        mirror: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> AddedSequenceElement:
        """Add an element to the video/image sequence on the video output; returns a SequenceElementId.

        Access: operator.
        """
        return self._run(
            OPS.add_sequence_element,
            None,
            {"schemaversion": schemaversion, "source": source, "duration": duration, "mirror": mirror},
            request_options,
        )

    def remove_sequence_element(
        self, sequenceelementid: int, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> None:
        """Remove an element from the video or image sequence. Access: operator."""
        self._run(
            OPS.remove_sequence_element,
            None,
            {"schemaversion": schemaversion, "sequenceelementid": sequenceelementid},
            request_options,
        )

    @overload
    def update_sequence_element(
        self, request: UpdateSequenceElementRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def update_sequence_element(
        self,
        sequenceelementid: int,
        /,
        *,
        schemaversion: int,
        sourceid: str | MISSING = MISSING,
        duration: int | MISSING = MISSING,
        mirror: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def update_sequence_element(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Update an element in the video or image sequence.

        At least one of sourceid, duration and mirror must be given.

        Changes only the fields given. Access: operator.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, UpdateSequenceElementRequest):
            kwargs = {**dict(zip(("sequenceelementid",), (request, *args), strict=False)), **kwargs}
            request = None
        self._run(OPS.update_sequence_element, request, kwargs, request_options)

    def get_sequence(self, *, schemaversion: int, request_options: RequestOptions | None = None) -> Sequence:
        """Get the current video sources configured in a sequence, in sequence order.

        Access: operator.
        """
        return self._run(OPS.get_sequence, None, {"schemaversion": schemaversion}, request_options)

    def clear_sequence(self, *, schemaversion: int, request_options: RequestOptions | None = None) -> None:
        """Remove the sequence. Access: operator."""
        self._run(OPS.clear_sequence, None, {"schemaversion": schemaversion}, request_options)

    def get_quad_view(self, *, schemaversion: int, request_options: RequestOptions | None = None) -> QuadView:
        """Get the video sources configured in a quad view (top left, top right, bottom left, bottom right).

        Access: operator.
        """
        return self._run(OPS.get_quad_view, None, {"schemaversion": schemaversion}, request_options)

    def set_quad_view(
        self, id: list[str], *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> None:
        """Configure and enable a quad view of video sources for the video output.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_quad_view, None, {"schemaversion": schemaversion, "id": id}, request_options)

    def get_rotation(self, *, schemaversion: int, request_options: RequestOptions | None = None) -> Rotations:
        """Get the current rotation and available rotations on the video output. Access: operator."""
        return self._run(OPS.get_rotation, None, {"schemaversion": schemaversion}, request_options)

    def set_rotation(self, rotation: int, *, schemaversion: int, request_options: RequestOptions | None = None) -> None:
        """Select a rotation on the video output (the supported rotations come from get_rotation).

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_rotation, None, {"schemaversion": schemaversion, "rotation": rotation}, request_options)

    def get_source_settings_enabled(
        self, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> SourceSettings:
        """Get whether the Image-parameter settings are used on each available video source.

        Access: operator.
        """
        return self._run(OPS.get_source_settings_enabled, None, {"schemaversion": schemaversion}, request_options)

    def set_source_settings_enabled(
        self, *, schemaversion: int, id: str, enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable mirroring, rotation and overlays (Image-parameter settings) on the selected video source.

        Changes only the fields given. Access: operator.
        """
        self._run(
            OPS.set_source_settings_enabled,
            None,
            {"schemaversion": schemaversion, "id": id, "enabled": enabled},
            request_options,
        )

    def get_supported(self, *, schemaversion: int, request_options: RequestOptions | None = None) -> SupportedCgis:
        """Get the supported CGI APIs for the product. Access: operator."""
        return self._run(OPS.get_supported, None, {"schemaversion": schemaversion}, request_options)

    def get_active_mode(self, *, schemaversion: int, request_options: RequestOptions | None = None) -> ActiveModes:
        """Get all supported modes and whether each is active. Access: operator."""
        return self._run(OPS.get_active_mode, None, {"schemaversion": schemaversion}, request_options)

    def set_active_mode(
        self,
        mode: Literal["source", "sequence", "quad", "PiP"],
        *,
        schemaversion: int,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the mode (source, sequence, quad or PiP).

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_active_mode, None, {"schemaversion": schemaversion, "mode": mode}, request_options)

    def get_pip(self, *, schemaversion: int, request_options: RequestOptions | None = None) -> PipSettings:
        """Return the current and available PiP (picture-in-picture) settings of the video output.

        Access: operator.
        """
        return self._run(OPS.get_pip, None, {"schemaversion": schemaversion}, request_options)

    @overload
    def set_pip(self, request: SetPipRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def set_pip(
        self,
        /,
        *,
        schemaversion: int,
        bordercolor: list[Annotated[float, Field(ge=0, le=1)]] | MISSING = MISSING,
        borderenabled: bool | MISSING = MISSING,
        borderweight: list[Annotated[float, Field(ge=0, le=1)]] | MISSING = MISSING,
        height: float | MISSING = MISSING,
        mainviewmirroring: bool | MISSING = MISSING,
        mainviewrotation: Literal[0, 180] | MISSING = MISSING,
        mainviewsource: int | MISSING = MISSING,
        position: Literal["top_left", "top_right", "bottom_left", "bottom_right"] | MISSING = MISSING,
        pipmirroring: bool | MISSING = MISSING,
        piprotation: Literal[0, 180] | MISSING = MISSING,
        pipsource: int | MISSING = MISSING,
        width: float | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_pip(
        self, request: SetPipRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Configure the PiP (picture-in-picture) parameters.

        Only the given parameters change.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_pip, request, kwargs, request_options)

    def get_dynamic_overlays(
        self, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> DynamicOverlays:
        """Return the current dynamic overlay setting. Access: operator."""
        return self._run(OPS.get_dynamic_overlays, None, {"schemaversion": schemaversion}, request_options)

    def set_dynamic_overlays(
        self, dynamicoverlays: bool, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable dynamic overlays; mirrors dynamic overlays to HDMI outputs.

        Changes only the fields given. Access: operator.
        """
        self._run(
            OPS.set_dynamic_overlays,
            None,
            {"schemaversion": schemaversion, "dynamicoverlays": dynamicoverlays},
            request_options,
        )


class AsyncVideoOutputApi(AsyncApi):
    """Video output API (``video-output``)."""

    INFO = INFO

    async def get_schema_versions(
        self, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> SchemaVersions:
        """Retrieve the supported XML schema versions. Access: operator."""
        return await self._run(OPS.get_schema_versions, None, {"schemaversion": schemaversion}, request_options)

    async def get_video_sources(
        self, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> VideoSources:
        """Retrieve available video sources; sources used as video output are marked active.

        Access: operator.
        """
        return await self._run(OPS.get_video_sources, None, {"schemaversion": schemaversion}, request_options)

    async def set_video_source(
        self, id: str, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> None:
        """Set the video source to display as video output.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_video_source, None, {"schemaversion": schemaversion, "id": id}, request_options)

    async def get_mirroring(self, *, schemaversion: int, request_options: RequestOptions | None = None) -> Mirroring:
        """Check if the video output is mirrored. Access: operator."""
        return await self._run(OPS.get_mirroring, None, {"schemaversion": schemaversion}, request_options)

    async def set_mirroring(
        self, mirroringenabled: bool, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> None:
        """Mirror the video output (recordings and other streams are not affected).

        Changes only the fields given. Access: operator.
        """
        await self._run(
            OPS.set_mirroring,
            None,
            {"schemaversion": schemaversion, "mirroringenabled": mirroringenabled},
            request_options,
        )

    async def add_sequence_element(
        self,
        *,
        schemaversion: int,
        source: str,
        duration: int,
        mirror: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> AddedSequenceElement:
        """Add an element to the video/image sequence on the video output; returns a SequenceElementId.

        Access: operator.
        """
        return await self._run(
            OPS.add_sequence_element,
            None,
            {"schemaversion": schemaversion, "source": source, "duration": duration, "mirror": mirror},
            request_options,
        )

    async def remove_sequence_element(
        self, sequenceelementid: int, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> None:
        """Remove an element from the video or image sequence. Access: operator."""
        await self._run(
            OPS.remove_sequence_element,
            None,
            {"schemaversion": schemaversion, "sequenceelementid": sequenceelementid},
            request_options,
        )

    @overload
    async def update_sequence_element(
        self, request: UpdateSequenceElementRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def update_sequence_element(
        self,
        sequenceelementid: int,
        /,
        *,
        schemaversion: int,
        sourceid: str | MISSING = MISSING,
        duration: int | MISSING = MISSING,
        mirror: bool | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def update_sequence_element(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Update an element in the video or image sequence.

        At least one of sourceid, duration and mirror must be given.

        Changes only the fields given. Access: operator.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, UpdateSequenceElementRequest):
            kwargs = {**dict(zip(("sequenceelementid",), (request, *args), strict=False)), **kwargs}
            request = None
        await self._run(OPS.update_sequence_element, request, kwargs, request_options)

    async def get_sequence(self, *, schemaversion: int, request_options: RequestOptions | None = None) -> Sequence:
        """Get the current video sources configured in a sequence, in sequence order.

        Access: operator.
        """
        return await self._run(OPS.get_sequence, None, {"schemaversion": schemaversion}, request_options)

    async def clear_sequence(self, *, schemaversion: int, request_options: RequestOptions | None = None) -> None:
        """Remove the sequence. Access: operator."""
        await self._run(OPS.clear_sequence, None, {"schemaversion": schemaversion}, request_options)

    async def get_quad_view(self, *, schemaversion: int, request_options: RequestOptions | None = None) -> QuadView:
        """Get the video sources configured in a quad view (top left, top right, bottom left, bottom right).

        Access: operator.
        """
        return await self._run(OPS.get_quad_view, None, {"schemaversion": schemaversion}, request_options)

    async def set_quad_view(
        self, id: list[str], *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> None:
        """Configure and enable a quad view of video sources for the video output.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_quad_view, None, {"schemaversion": schemaversion, "id": id}, request_options)

    async def get_rotation(self, *, schemaversion: int, request_options: RequestOptions | None = None) -> Rotations:
        """Get the current rotation and available rotations on the video output. Access: operator."""
        return await self._run(OPS.get_rotation, None, {"schemaversion": schemaversion}, request_options)

    async def set_rotation(
        self, rotation: int, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> None:
        """Select a rotation on the video output (the supported rotations come from get_rotation).

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_rotation, None, {"schemaversion": schemaversion, "rotation": rotation}, request_options)

    async def get_source_settings_enabled(
        self, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> SourceSettings:
        """Get whether the Image-parameter settings are used on each available video source.

        Access: operator.
        """
        return await self._run(OPS.get_source_settings_enabled, None, {"schemaversion": schemaversion}, request_options)

    async def set_source_settings_enabled(
        self, *, schemaversion: int, id: str, enabled: bool, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable mirroring, rotation and overlays (Image-parameter settings) on the selected video source.

        Changes only the fields given. Access: operator.
        """
        await self._run(
            OPS.set_source_settings_enabled,
            None,
            {"schemaversion": schemaversion, "id": id, "enabled": enabled},
            request_options,
        )

    async def get_supported(
        self, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> SupportedCgis:
        """Get the supported CGI APIs for the product. Access: operator."""
        return await self._run(OPS.get_supported, None, {"schemaversion": schemaversion}, request_options)

    async def get_active_mode(
        self, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> ActiveModes:
        """Get all supported modes and whether each is active. Access: operator."""
        return await self._run(OPS.get_active_mode, None, {"schemaversion": schemaversion}, request_options)

    async def set_active_mode(
        self,
        mode: Literal["source", "sequence", "quad", "PiP"],
        *,
        schemaversion: int,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Set the mode (source, sequence, quad or PiP).

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_active_mode, None, {"schemaversion": schemaversion, "mode": mode}, request_options)

    async def get_pip(self, *, schemaversion: int, request_options: RequestOptions | None = None) -> PipSettings:
        """Return the current and available PiP (picture-in-picture) settings of the video output.

        Access: operator.
        """
        return await self._run(OPS.get_pip, None, {"schemaversion": schemaversion}, request_options)

    @overload
    async def set_pip(self, request: SetPipRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    async def set_pip(
        self,
        /,
        *,
        schemaversion: int,
        bordercolor: list[Annotated[float, Field(ge=0, le=1)]] | MISSING = MISSING,
        borderenabled: bool | MISSING = MISSING,
        borderweight: list[Annotated[float, Field(ge=0, le=1)]] | MISSING = MISSING,
        height: float | MISSING = MISSING,
        mainviewmirroring: bool | MISSING = MISSING,
        mainviewrotation: Literal[0, 180] | MISSING = MISSING,
        mainviewsource: int | MISSING = MISSING,
        position: Literal["top_left", "top_right", "bottom_left", "bottom_right"] | MISSING = MISSING,
        pipmirroring: bool | MISSING = MISSING,
        piprotation: Literal[0, 180] | MISSING = MISSING,
        pipsource: int | MISSING = MISSING,
        width: float | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_pip(
        self, request: SetPipRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Configure the PiP (picture-in-picture) parameters.

        Only the given parameters change.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_pip, request, kwargs, request_options)

    async def get_dynamic_overlays(
        self, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> DynamicOverlays:
        """Return the current dynamic overlay setting. Access: operator."""
        return await self._run(OPS.get_dynamic_overlays, None, {"schemaversion": schemaversion}, request_options)

    async def set_dynamic_overlays(
        self, dynamicoverlays: bool, *, schemaversion: int, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable dynamic overlays; mirrors dynamic overlays to HDMI outputs.

        Changes only the fields given. Access: operator.
        """
        await self._run(
            OPS.set_dynamic_overlays,
            None,
            {"schemaversion": schemaversion, "dynamicoverlays": dynamicoverlays},
            request_options,
        )
