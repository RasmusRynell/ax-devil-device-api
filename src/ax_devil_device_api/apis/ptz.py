# GENERATED from specs/apis/network-video/ptz-control.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Control and configure mechanical and digital pan, tilt and zoom (focus, iris, brightness, presets, OSD menu, IR cut filter, backlight).

Docs: https://developer.axis.com/vapix/network-video/pantiltzoom-api/
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, Text, TextKv
from ._base import AsyncApi, SyncApi, bind_positional

# ---------------------------------------------------------------------------
# Models

Camera = Annotated[int, Field(ge=1)]
CameraOrAll = Annotated[str, Field(pattern="^([0-9]+|all)$")]
ImageRotation = Literal[0, 90, 180, 270]
Speed = Annotated[int, Field(ge=1, le=100)]
OnOff = Literal["on", "off"]
PresetName = Annotated[str, Field(max_length=31, pattern='^[^"<>~:]*$')]


class PtzLimits(Model):
    """The PTZ limits of the product. Which values are returned depends on the product and its drivers."""

    min_pan: float | None = Field(default=None, validation_alias="MinPan", serialization_alias="MinPan")
    max_pan: float | None = Field(default=None, validation_alias="MaxPan", serialization_alias="MaxPan")
    min_tilt: float | None = Field(default=None, validation_alias="MinTilt", serialization_alias="MinTilt")
    max_tilt: float | None = Field(default=None, validation_alias="MaxTilt", serialization_alias="MaxTilt")
    min_zoom: int | None = Field(default=None, validation_alias="MinZoom", serialization_alias="MinZoom")
    max_zoom: int | None = Field(default=None, validation_alias="MaxZoom", serialization_alias="MaxZoom")
    min_iris: int | None = Field(default=None, validation_alias="MinIris", serialization_alias="MinIris")
    max_iris: int | None = Field(default=None, validation_alias="MaxIris", serialization_alias="MaxIris")
    min_focus: int | None = Field(default=None, validation_alias="MinFocus", serialization_alias="MinFocus")
    max_focus: int | None = Field(default=None, validation_alias="MaxFocus", serialization_alias="MaxFocus")
    min_field_angle: float | None = Field(
        default=None, validation_alias="MinFieldAngle", serialization_alias="MinFieldAngle"
    )
    max_field_angle: float | None = Field(
        default=None, validation_alias="MaxFieldAngle", serialization_alias="MaxFieldAngle"
    )
    min_brightness: int | None = Field(
        default=None, validation_alias="MinBrightness", serialization_alias="MinBrightness"
    )
    max_brightness: int | None = Field(
        default=None, validation_alias="MaxBrightness", serialization_alias="MaxBrightness"
    )


class PtzPosition(Model):
    """The current position. Which values are returned depends on the product and its drivers."""

    pan: float | None = None
    """The absolute pan position in degrees."""
    tilt: float | None = None
    """The absolute tilt position in degrees."""
    zoom: int | None = None
    """The absolute zoom position."""
    autofocus: OnOff | None = None
    autoiris: OnOff | None = None


class PtzSpeed(Model):
    speed: int | None = None
    """The pan and tilt speed."""


class MoveRequest(Model):
    move: Literal["home", "up", "down", "left", "right", "upleft", "upright", "downleft", "downright", "stop"]
    """The direction."""
    camera: Camera | None = None
    speed: Speed | None = None
    imagerotation: ImageRotation | None = None


class CenterRequest(Model):
    center: list[int] = Field(min_length=2, max_length=2)
    """The x and y pixel coordinates in the client video stream."""
    imagewidth: int | None = Field(default=None, ge=1)
    """Required if the displayed image width differs from the default (product specific) image width."""
    imageheight: int | None = Field(default=None, ge=1)
    """Required if the displayed image height differs from the default (product specific) image height."""
    camera: Camera | None = None
    imagerotation: ImageRotation | None = None


class AreaZoomRequest(Model):
    area: list[int] = Field(validation_alias="areazoom", serialization_alias="areazoom", min_length=3, max_length=3)
    """The x and y pixel coordinates and the zoom factor z (at least 1)."""
    imagewidth: int | None = Field(default=None, ge=1)
    """Required if the displayed image width differs from the default (product specific) image width."""
    imageheight: int | None = Field(default=None, ge=1)
    """Required if the displayed image height differs from the default (product specific) image height."""
    camera: Camera | None = None
    imagerotation: ImageRotation | None = None


class AbsoluteMoveRequest(Model):
    pan: float | None = Field(default=None, ge=-180.0, le=180.0)
    """The absolute pan position in degrees."""
    tilt: float | None = Field(default=None, ge=-180.0, le=180.0)
    """The absolute tilt position in degrees."""
    zoom: int | None = Field(default=None, ge=1, le=19999)
    """The absolute zoom position; a high value zooms in. The range is 1 to 9999, or 1 to 19999 when Support.S#.DigitalZoom is true."""
    focus: int | None = Field(default=None, ge=1, le=9999)
    """The absolute focus position; a high value focuses far (driver specific)."""
    iris: int | None = Field(default=None, ge=1, le=9999)
    """The absolute iris position; a high value opens the iris."""
    brightness: int | None = Field(default=None, ge=1, le=9999)
    """The absolute brightness position; a high value is brighter."""
    speed: Speed | None = None
    camera: Camera | None = None
    imagerotation: ImageRotation | None = None


class RelativeMoveRequest(Model):
    rpan: float | None = Field(default=None, ge=-360.0, le=360.0)
    """Pan this many degrees."""
    rtilt: float | None = Field(default=None, ge=-360.0, le=360.0)
    """Tilt this many degrees."""
    rzoom: int | None = Field(default=None, ge=-19999, le=19999)
    """Zoom this many steps. The range is -9999 to 9999, or -19999 to 19999 when Support.S#.DigitalZoom is true."""
    rfocus: int | None = Field(default=None, ge=-9999, le=9999)
    """Move the focus this many steps."""
    riris: int | None = Field(default=None, ge=-9999, le=9999)
    """Move the iris this many steps."""
    rbrightness: int | None = Field(default=None, ge=-9999, le=9999)
    """Move the brightness this many steps."""
    speed: Speed | None = None
    camera: Camera | None = None
    imagerotation: ImageRotation | None = None


class ContinuousMoveRequest(Model):
    pan_tilt: list[Annotated[int, Field(ge=-100, le=100)]] | None = Field(
        default=None,
        validation_alias="continuouspantiltmove",
        serialization_alias="continuouspantiltmove",
        min_length=2,
        max_length=2,
    )
    """The pan speed and the tilt speed. ``[0, 0]`` stops the movement."""
    zoom: int | None = Field(
        default=None, validation_alias="continuouszoommove", serialization_alias="continuouszoommove", ge=-100, le=100
    )
    """The zoom speed."""
    focus: int | None = Field(
        default=None, validation_alias="continuousfocusmove", serialization_alias="continuousfocusmove", ge=-100, le=100
    )
    """The focus speed."""
    iris: int | None = Field(
        default=None, validation_alias="continuousirismove", serialization_alias="continuousirismove", ge=-100, le=100
    )
    """The iris speed."""
    brightness: int | None = Field(
        default=None,
        validation_alias="continuousbrightnessmove",
        serialization_alias="continuousbrightnessmove",
        ge=-100,
        le=100,
    )
    """The brightness speed."""
    proportionalspeed: Literal["disabled"] | None = None
    """Disables proportional speed for this command. Only supported on mechanical PTZ domes with Properties.PTZ.DigitalPTZ=no and Properties.PTZ.DriverManagement=no (API version 1.1)."""
    camera: Camera | None = None
    imagerotation: ImageRotation | None = None


class SetAutofocusRequest(Model):
    autofocus: OnOff
    camera: Camera | None = None


class SetAutoirisRequest(Model):
    autoiris: OnOff
    camera: Camera | None = None


class SetIrCutFilterRequest(Model):
    ircutfilter: Literal["auto", "on", "off"]
    camera: Camera | None = None


class SetBacklightRequest(Model):
    backlight: OnOff
    camera: Camera | None = None


class ActivateAuxiliaryRequest(Model):
    function: str = Field(validation_alias="auxiliary", serialization_alias="auxiliary")
    """The name of the device specific function."""
    camera: Camera | None = None


class GoToServerPresetNameRequest(Model):
    name: str = Field(validation_alias="gotoserverpresetname", serialization_alias="gotoserverpresetname")
    """The preset name."""
    camera: Camera | None = None
    speed: Speed | None = None


class GoToServerPresetNumberRequest(Model):
    number: int = Field(validation_alias="gotoserverpresetno", serialization_alias="gotoserverpresetno", ge=1)
    """The preset position number."""
    camera: Camera | None = None
    speed: Speed | None = None


class GoToDevicePresetRequest(Model):
    preset: int = Field(validation_alias="gotodevicepreset", serialization_alias="gotodevicepreset")
    """The device specific preset position number."""
    camera: Camera | None = None
    speed: Speed | None = None


class GetLimitsRequest(Model):
    camera: Camera | None = None


class GetModeRequest(Model):
    camera: Camera | None = None


class GetPositionRequest(Model):
    camera: Camera | None = None


class GetSpeedRequest(Model):
    camera: Camera | None = None


class ListPresetsRequest(Model):
    camera: CameraOrAll | None = None
    format: Literal["json"] | None = None
    """Return JSON instead of plain text."""


class ListAllPresetsRequest(Model):
    format: Literal["json"] | None = None
    """Return JSON instead of plain text."""


class GetPresetDataRequest(Model):
    camera: CameraOrAll | None = None
    format: Literal["json"] | None = None
    """Return JSON instead of plain text."""


class ListAuxiliaryCommandsRequest(Model):
    camera: Camera | None = None
    format: Literal["json"] | None = None
    """Return JSON instead of plain text."""


class GetAttributesRequest(Model):
    camera: CameraOrAll | None = None
    format: Literal["json"] | None = None
    """Return JSON instead of plain text."""
    group: Literal["zoom", "focus", "speed", "speeddry"] | None = None
    """The attribute group. All attributes are returned if omitted."""


class GetInfoRequest(Model):
    camera: Camera | None = None


class GetDriverNameRequest(Model):
    camera: Camera | None = None


class SetServerPresetNameRequest(Model):
    name: PresetName = Field(validation_alias="setserverpresetname", serialization_alias="setserverpresetname")
    home: Literal["yes"] | None = None
    """Make the position the home position of the product."""
    camera: Camera | None = None


class SetServerPresetNumberRequest(Model):
    number: int = Field(validation_alias="setserverpresetno", serialization_alias="setserverpresetno", ge=1)
    """The preset position number."""
    home: Literal["yes"] | None = None
    """Make the position the home position of the product."""
    camera: Camera | None = None


class RenameServerPresetRequest(Model):
    number: int = Field(validation_alias="renameserverpresetno", serialization_alias="renameserverpresetno", ge=1)
    """The number of the preset to rename."""
    new_name: PresetName = Field(validation_alias="newname", serialization_alias="newname")
    camera: Camera | None = None


class RemoveServerPresetNameRequest(Model):
    name: PresetName = Field(validation_alias="removeserverpresetname", serialization_alias="removeserverpresetname")
    camera: Camera | None = None


class RemoveServerPresetNumberRequest(Model):
    number: int = Field(validation_alias="removeserverpresetno", serialization_alias="removeserverpresetno", ge=1)
    """The preset position number."""
    camera: Camera | None = None


class RemoveAllServerPresetsRequest(Model):
    camera: CameraOrAll | None = None


class SetDevicePresetRequest(Model):
    preset: int = Field(validation_alias="setdevicepreset", serialization_alias="setdevicepreset")
    """The device specific preset position number."""
    camera: Camera | None = None


class ControlOsdMenuRequest(Model):
    command: Literal["open", "close", "up", "down", "left", "right", "select", "back"] = Field(
        validation_alias="osdmenu", serialization_alias="osdmenu"
    )
    """The OSD menu command."""
    camera: Camera | None = None


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/com/ptz.cgi"

INFO = ApiInfo(
    id="ptz-control",
    name="PTZ control API",
    family=Family.CGI,
    discovery=(
        ApiDiscovery("ptz-control"),
        ParamDiscovery("Properties.API.PTZ.Presets.Version", "2.00"),
        ParamDiscovery("Properties.PTZ.PTZ", "yes"),
        ParamDiscovery("Properties.PTZ.DigitalPTZ", "yes"),
        ParamDiscovery("Properties.Overview.Overview", "yes"),
        ParamDiscovery("Properties.Overview.MechanicalHybrid", "yes"),
        ParamDiscovery("Properties.PTZ.EmbeddedDrivers", "yes"),
    ),
    requires_firmware="5.20",
    docs=("https://developer.axis.com/vapix/network-video/pantiltzoom-api/",),
)


class OPS:
    move = Operation(
        INFO,
        "move",
        CgiBinding(
            PATH, args=(CgiArg("move"), CgiArg("camera"), CgiArg("speed"), CgiArg("imagerotation")), reply=Text()
        ),
        params=MoveRequest,
        access="viewer",
        effect="action",
    )
    center = Operation(
        INFO,
        "center",
        CgiBinding(
            PATH,
            args=(
                CgiArg("center", style="csv"),
                CgiArg("imagewidth"),
                CgiArg("imageheight"),
                CgiArg("camera"),
                CgiArg("imagerotation"),
            ),
            reply=Text(),
        ),
        params=CenterRequest,
        access="viewer",
        effect="action",
    )
    area_zoom = Operation(
        INFO,
        "area_zoom",
        CgiBinding(
            PATH,
            args=(
                CgiArg("area", wire="areazoom", style="csv"),
                CgiArg("imagewidth"),
                CgiArg("imageheight"),
                CgiArg("camera"),
                CgiArg("imagerotation"),
            ),
            reply=Text(),
        ),
        params=AreaZoomRequest,
        access="viewer",
        effect="action",
    )
    absolute_move = Operation(
        INFO,
        "absolute_move",
        CgiBinding(
            PATH,
            args=(
                CgiArg("pan"),
                CgiArg("tilt"),
                CgiArg("zoom"),
                CgiArg("focus"),
                CgiArg("iris"),
                CgiArg("brightness"),
                CgiArg("speed"),
                CgiArg("camera"),
                CgiArg("imagerotation"),
            ),
            reply=Text(),
        ),
        params=AbsoluteMoveRequest,
        access="viewer",
        effect="action",
    )
    relative_move = Operation(
        INFO,
        "relative_move",
        CgiBinding(
            PATH,
            args=(
                CgiArg("rpan"),
                CgiArg("rtilt"),
                CgiArg("rzoom"),
                CgiArg("rfocus"),
                CgiArg("riris"),
                CgiArg("rbrightness"),
                CgiArg("speed"),
                CgiArg("camera"),
                CgiArg("imagerotation"),
            ),
            reply=Text(),
        ),
        params=RelativeMoveRequest,
        access="viewer",
        effect="action",
    )
    continuous_move = Operation(
        INFO,
        "continuous_move",
        CgiBinding(
            PATH,
            args=(
                CgiArg("pan_tilt", wire="continuouspantiltmove", style="csv"),
                CgiArg("zoom", wire="continuouszoommove"),
                CgiArg("focus", wire="continuousfocusmove"),
                CgiArg("iris", wire="continuousirismove"),
                CgiArg("brightness", wire="continuousbrightnessmove"),
                CgiArg("proportionalspeed"),
                CgiArg("camera"),
                CgiArg("imagerotation"),
            ),
            reply=Text(),
        ),
        params=ContinuousMoveRequest,
        access="viewer",
        effect="action",
    )
    set_autofocus = Operation(
        INFO,
        "set_autofocus",
        CgiBinding(PATH, args=(CgiArg("autofocus"), CgiArg("camera")), reply=Text()),
        params=SetAutofocusRequest,
        access="viewer",
        effect="write",
        write="patch",
    )
    set_autoiris = Operation(
        INFO,
        "set_autoiris",
        CgiBinding(PATH, args=(CgiArg("autoiris"), CgiArg("camera")), reply=Text()),
        params=SetAutoirisRequest,
        access="viewer",
        effect="write",
        write="patch",
    )
    set_ir_cut_filter = Operation(
        INFO,
        "set_ir_cut_filter",
        CgiBinding(PATH, args=(CgiArg("ircutfilter"), CgiArg("camera")), reply=Text()),
        params=SetIrCutFilterRequest,
        access="viewer",
        effect="write",
        write="patch",
    )
    set_backlight = Operation(
        INFO,
        "set_backlight",
        CgiBinding(PATH, args=(CgiArg("backlight"), CgiArg("camera")), reply=Text()),
        params=SetBacklightRequest,
        access="viewer",
        effect="write",
        write="patch",
    )
    activate_auxiliary = Operation(
        INFO,
        "activate_auxiliary",
        CgiBinding(PATH, args=(CgiArg("function", wire="auxiliary"), CgiArg("camera")), reply=Text()),
        params=ActivateAuxiliaryRequest,
        access="viewer",
        effect="action",
    )
    go_to_server_preset_name = Operation(
        INFO,
        "go_to_server_preset_name",
        CgiBinding(
            PATH, args=(CgiArg("name", wire="gotoserverpresetname"), CgiArg("camera"), CgiArg("speed")), reply=Text()
        ),
        params=GoToServerPresetNameRequest,
        access="viewer",
        effect="action",
    )
    go_to_server_preset_number = Operation(
        INFO,
        "go_to_server_preset_number",
        CgiBinding(
            PATH, args=(CgiArg("number", wire="gotoserverpresetno"), CgiArg("camera"), CgiArg("speed")), reply=Text()
        ),
        params=GoToServerPresetNumberRequest,
        access="viewer",
        effect="action",
    )
    go_to_device_preset = Operation(
        INFO,
        "go_to_device_preset",
        CgiBinding(
            PATH, args=(CgiArg("preset", wire="gotodevicepreset"), CgiArg("camera"), CgiArg("speed")), reply=Text()
        ),
        params=GoToDevicePresetRequest,
        access="viewer",
        effect="action",
    )
    get_limits = Operation(
        INFO,
        "get_limits",
        CgiBinding(PATH, fixed_query=(("query", "limits"),), args=(CgiArg("camera"),), reply=TextKv()),
        params=GetLimitsRequest,
        result=PtzLimits,
        access="viewer",
        effect="read",
    )
    get_mode = Operation(
        INFO,
        "get_mode",
        CgiBinding(PATH, fixed_query=(("query", "mode"),), args=(CgiArg("camera"),), reply=Text()),
        params=GetModeRequest,
        result=str,
        access="viewer",
        effect="read",
    )
    get_position = Operation(
        INFO,
        "get_position",
        CgiBinding(PATH, fixed_query=(("query", "position"),), args=(CgiArg("camera"),), reply=TextKv()),
        params=GetPositionRequest,
        result=PtzPosition,
        access="viewer",
        effect="read",
    )
    get_speed = Operation(
        INFO,
        "get_speed",
        CgiBinding(PATH, fixed_query=(("query", "speed"),), args=(CgiArg("camera"),), reply=TextKv()),
        params=GetSpeedRequest,
        result=PtzSpeed,
        access="viewer",
        effect="read",
    )
    list_presets = Operation(
        INFO,
        "list_presets",
        CgiBinding(
            PATH, fixed_query=(("query", "presetposcam"),), args=(CgiArg("camera"), CgiArg("format")), reply=Text()
        ),
        params=ListPresetsRequest,
        result=str,
        access="viewer",
        effect="read",
    )
    list_all_presets = Operation(
        INFO,
        "list_all_presets",
        CgiBinding(PATH, fixed_query=(("query", "presetposall"),), args=(CgiArg("format"),), reply=Text()),
        params=ListAllPresetsRequest,
        result=str,
        access="viewer",
        effect="read",
    )
    get_preset_data = Operation(
        INFO,
        "get_preset_data",
        CgiBinding(
            PATH, fixed_query=(("query", "presetposcamdata"),), args=(CgiArg("camera"), CgiArg("format")), reply=Text()
        ),
        params=GetPresetDataRequest,
        result=str,
        access="viewer",
        effect="read",
    )
    list_auxiliary_commands = Operation(
        INFO,
        "list_auxiliary_commands",
        CgiBinding(
            PATH, fixed_query=(("query", "auxiliary"),), args=(CgiArg("camera"), CgiArg("format")), reply=Text()
        ),
        params=ListAuxiliaryCommandsRequest,
        result=str,
        access="viewer",
        effect="read",
    )
    get_attributes = Operation(
        INFO,
        "get_attributes",
        CgiBinding(
            PATH,
            fixed_query=(("query", "attributes"),),
            args=(CgiArg("camera"), CgiArg("format"), CgiArg("group")),
            reply=Text(),
        ),
        params=GetAttributesRequest,
        result=str,
        access="viewer",
        effect="read",
    )
    get_info = Operation(
        INFO,
        "get_info",
        CgiBinding(PATH, fixed_query=(("info", "1"),), args=(CgiArg("camera"),), reply=Text()),
        params=GetInfoRequest,
        result=str,
        access="viewer",
        effect="read",
    )
    get_driver_name = Operation(
        INFO,
        "get_driver_name",
        CgiBinding(PATH, fixed_query=(("whoami", "1"),), args=(CgiArg("camera"),), reply=Text()),
        params=GetDriverNameRequest,
        result=str,
        access="viewer",
        effect="read",
    )
    set_server_preset_name = Operation(
        INFO,
        "set_server_preset_name",
        CgiBinding(
            "/axis-cgi/com/ptzconfig.cgi",
            args=(CgiArg("name", wire="setserverpresetname"), CgiArg("home"), CgiArg("camera")),
            reply=Text(),
        ),
        params=SetServerPresetNameRequest,
        access="admin",
        effect="write",
        write="create",
    )
    set_server_preset_number = Operation(
        INFO,
        "set_server_preset_number",
        CgiBinding(
            "/axis-cgi/com/ptzconfig.cgi",
            args=(CgiArg("number", wire="setserverpresetno"), CgiArg("home"), CgiArg("camera")),
            reply=Text(),
        ),
        params=SetServerPresetNumberRequest,
        access="admin",
        effect="write",
        write="create",
    )
    rename_server_preset = Operation(
        INFO,
        "rename_server_preset",
        CgiBinding(
            "/axis-cgi/com/ptzconfig.cgi",
            args=(CgiArg("number", wire="renameserverpresetno"), CgiArg("new_name", wire="newname"), CgiArg("camera")),
            reply=Text(),
        ),
        params=RenameServerPresetRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    remove_server_preset_name = Operation(
        INFO,
        "remove_server_preset_name",
        CgiBinding(
            "/axis-cgi/com/ptzconfig.cgi",
            args=(CgiArg("name", wire="removeserverpresetname"), CgiArg("camera")),
            reply=Text(),
        ),
        params=RemoveServerPresetNameRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    remove_server_preset_number = Operation(
        INFO,
        "remove_server_preset_number",
        CgiBinding(
            "/axis-cgi/com/ptzconfig.cgi",
            args=(CgiArg("number", wire="removeserverpresetno"), CgiArg("camera")),
            reply=Text(),
        ),
        params=RemoveServerPresetNumberRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    remove_all_server_presets = Operation(
        INFO,
        "remove_all_server_presets",
        CgiBinding(
            "/axis-cgi/com/ptzconfig.cgi",
            fixed_query=(("removeallserverpresets", "yes"),),
            args=(CgiArg("camera"),),
            reply=Text(),
        ),
        params=RemoveAllServerPresetsRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    set_device_preset = Operation(
        INFO,
        "set_device_preset",
        CgiBinding(
            "/axis-cgi/com/ptzconfig.cgi",
            args=(CgiArg("preset", wire="setdevicepreset"), CgiArg("camera")),
            reply=Text(),
        ),
        params=SetDevicePresetRequest,
        access="admin",
        effect="write",
        write="create",
    )
    control_osd_menu = Operation(
        INFO,
        "control_osd_menu",
        CgiBinding(
            "/axis-cgi/com/ptzconfig.cgi", args=(CgiArg("command", wire="osdmenu"), CgiArg("camera")), reply=Text()
        ),
        params=ControlOsdMenuRequest,
        access="admin",
        effect="action",
    )


# ---------------------------------------------------------------------------
# API classes


class PtzControlApi(SyncApi):
    """PTZ control API (``ptz-control``)."""

    INFO = INFO

    def move(
        self,
        move: Literal["home", "up", "down", "left", "right", "upleft", "upright", "downleft", "downright", "stop"],
        *,
        camera: Camera | MISSING = MISSING,
        speed: Speed | MISSING = MISSING,
        imagerotation: ImageRotation | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Move the image or the device in a direction, go to the home position or stop the pan and tilt movement.

        On absolute (digital) PTZ the image moves 25 % of the image field width in the direction; on
        relative PTZ the device moves roughly 50 to 90 degrees (driver specific). ``home`` moves to the home
        position and ``stop`` stops the pan and tilt movement.

        Access: viewer.
        """
        self._run(
            OPS.move,
            None,
            {"move": move, "camera": camera, "speed": speed, "imagerotation": imagerotation},
            request_options,
        )

    @overload
    def center(self, request: CenterRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def center(
        self,
        center: list[int],
        /,
        *,
        imagewidth: int | MISSING = MISSING,
        imageheight: int | MISSING = MISSING,
        camera: Camera | MISSING = MISSING,
        imagerotation: ImageRotation | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def center(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Center the camera on pixel coordinates of the client video stream. Access: viewer."""
        if request is MISSING:
            request = None
        elif args or not isinstance(request, CenterRequest):
            kwargs = bind_positional(OPS.center, ("center",), (request, *args), kwargs)
            request = None
        self._run(OPS.center, request, kwargs, request_options)

    @overload
    def area_zoom(self, request: AreaZoomRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def area_zoom(
        self,
        area: list[int],
        /,
        *,
        imagewidth: int | MISSING = MISSING,
        imageheight: int | MISSING = MISSING,
        camera: Camera | MISSING = MISSING,
        imagerotation: ImageRotation | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def area_zoom(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Center on pixel coordinates and zoom by a factor of z/100.

        A z above 100 zooms in (300 zooms in to a third of the current field of view); a z below 100 zooms
        out (50 zooms out to twice the field of view). On some products the precision improves when the lens
        offset parameters are calibrated.

        Access: viewer.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, AreaZoomRequest):
            kwargs = bind_positional(OPS.area_zoom, ("area",), (request, *args), kwargs)
            request = None
        self._run(OPS.area_zoom, request, kwargs, request_options)

    @overload
    def absolute_move(
        self, request: AbsoluteMoveRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def absolute_move(
        self,
        /,
        *,
        pan: float | MISSING = MISSING,
        tilt: float | MISSING = MISSING,
        zoom: int | MISSING = MISSING,
        focus: int | MISSING = MISSING,
        iris: int | MISSING = MISSING,
        brightness: int | MISSING = MISSING,
        speed: Speed | MISSING = MISSING,
        camera: Camera | MISSING = MISSING,
        imagerotation: ImageRotation | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def absolute_move(
        self,
        request: AbsoluteMoveRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Move pan, tilt, zoom, focus, iris and brightness to absolute positions.

        Several axes can be combined in one request. Float input to zoom, focus, iris and brightness is
        handled as an integer, with no guarantee on the rounding. On Panopsis products a position where the
        fisheye lens is visible switches the product to overview mode.

        Access: viewer.
        """
        self._run(OPS.absolute_move, request, kwargs, request_options)

    @overload
    def relative_move(
        self, request: RelativeMoveRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def relative_move(
        self,
        /,
        *,
        rpan: float | MISSING = MISSING,
        rtilt: float | MISSING = MISSING,
        rzoom: int | MISSING = MISSING,
        rfocus: int | MISSING = MISSING,
        riris: int | MISSING = MISSING,
        rbrightness: int | MISSING = MISSING,
        speed: Speed | MISSING = MISSING,
        camera: Camera | MISSING = MISSING,
        imagerotation: ImageRotation | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def relative_move(
        self,
        request: RelativeMoveRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Move pan, tilt, zoom, focus, iris and brightness relative to the current position.

        Several axes can be combined in one request. Positive rzoom zooms in, positive rfocus focuses far,
        positive riris opens the iris and positive rbrightness gives a brighter image. On Panopsis products
        the command has no effect in overview mode.

        Access: viewer.
        """
        self._run(OPS.relative_move, request, kwargs, request_options)

    @overload
    def continuous_move(
        self, request: ContinuousMoveRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def continuous_move(
        self,
        /,
        *,
        pan_tilt: list[Annotated[int, Field(ge=-100, le=100)]] | MISSING = MISSING,
        zoom: int | MISSING = MISSING,
        focus: int | MISSING = MISSING,
        iris: int | MISSING = MISSING,
        brightness: int | MISSING = MISSING,
        proportionalspeed: Literal["disabled"] | MISSING = MISSING,
        camera: Camera | MISSING = MISSING,
        imagerotation: ImageRotation | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def continuous_move(
        self,
        request: ContinuousMoveRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Start a continuous pan, tilt, zoom, focus, iris or brightness movement; 0 stops it.

        Speeds range from -100 to 100. Positive pan is right, positive tilt is up, positive zoom zooms in,
        positive focus focuses far, positive iris opens the iris and positive brightness gives a brighter
        image. On Panopsis products the zoom, focus, iris and brightness moves have no effect in overview
        mode.

        Access: viewer.
        """
        self._run(OPS.continuous_move, request, kwargs, request_options)

    def set_autofocus(
        self, autofocus: OnOff, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable auto focus. Changes only the fields given. Access: viewer."""
        self._run(OPS.set_autofocus, None, {"autofocus": autofocus, "camera": camera}, request_options)

    def set_autoiris(
        self, autoiris: OnOff, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable auto iris. Changes only the fields given. Access: viewer."""
        self._run(OPS.set_autoiris, None, {"autoiris": autoiris, "camera": camera}, request_options)

    def set_ir_cut_filter(
        self,
        ircutfilter: Literal["auto", "on", "off"],
        *,
        camera: Camera | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Control the IR cut filter.

        ``on`` applies the filter and blocks IR light, ``off`` removes it and lets IR light reach the
        sensor, ``auto`` switches depending on the lighting conditions (product and release dependent).

        Changes only the fields given. Access: viewer.
        """
        self._run(OPS.set_ir_cut_filter, None, {"ircutfilter": ircutfilter, "camera": camera}, request_options)

    def set_backlight(
        self, backlight: OnOff, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Control the backlight compensation.

        ``on`` is bright mode and ``off`` normal mode.

        Changes only the fields given. Access: viewer.
        """
        self._run(OPS.set_backlight, None, {"backlight": backlight, "camera": camera}, request_options)

    def activate_auxiliary(
        self, function: str, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Activate or deactivate a device specific auxiliary function.

        The function names are driver specific; see ``list_auxiliary_commands`` or ``get_info``.

        Access: viewer.
        """
        self._run(OPS.activate_auxiliary, None, {"function": function, "camera": camera}, request_options)

    def go_to_server_preset_name(
        self,
        name: str,
        *,
        camera: Camera | MISSING = MISSING,
        speed: Speed | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Move to the server preset with a name. Access: viewer."""
        self._run(OPS.go_to_server_preset_name, None, {"name": name, "camera": camera, "speed": speed}, request_options)

    def go_to_server_preset_number(
        self,
        number: int,
        *,
        camera: Camera | MISSING = MISSING,
        speed: Speed | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Move to the server preset with a number. Access: viewer."""
        self._run(
            OPS.go_to_server_preset_number, None, {"number": number, "camera": camera, "speed": speed}, request_options
        )

    def go_to_device_preset(
        self,
        preset: int,
        *,
        camera: Camera | MISSING = MISSING,
        speed: Speed | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Move to a preset stored in the device, bypassing the preset interface of the product.

        The preset position number is device specific and may also be a device specific special function.

        Access: viewer.
        """
        self._run(OPS.go_to_device_preset, None, {"preset": preset, "camera": camera, "speed": speed}, request_options)

    def get_limits(
        self, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> PtzLimits:
        """Get the PTZ limits of the product. Access: viewer."""
        return self._run(OPS.get_limits, None, {"camera": camera}, request_options)

    def get_mode(self, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None) -> str:
        """Get the current mode (overview or normal) of a product with Panopsis technology.

        Access: viewer.
        """
        return self._run(OPS.get_mode, None, {"camera": camera}, request_options)

    def get_position(
        self, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> PtzPosition:
        """Get the current PTZ position (driver specific). Access: viewer."""
        return self._run(OPS.get_position, None, {"camera": camera}, request_options)

    def get_speed(
        self, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> PtzSpeed:
        """Get the pan and tilt speed. Access: viewer."""
        return self._run(OPS.get_speed, None, {"camera": camera}, request_options)

    def list_presets(
        self,
        *,
        camera: CameraOrAll | MISSING = MISSING,
        format: Literal["json"] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """List the preset positions of a video channel.

        The text reply is ``Preset Positions for camera <n>`` followed by ``presetposno<n>=<name>`` lines,
        encoded as set by ``PTZ.ResponseEncoding``. With ``format=json`` the reply is JSON; both are
        returned as text.

        Access: viewer.
        """
        return self._run(OPS.list_presets, None, {"camera": camera, "format": format}, request_options)

    def list_all_presets(
        self, *, format: Literal["json"] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> str:
        """List the preset positions of all video channels.

        Plain text in the same form as ``list_presets``, one section per channel. With ``format=json`` the
        reply is JSON.

        Access: viewer.
        """
        return self._run(OPS.list_all_presets, None, {"format": format}, request_options)

    def get_preset_data(
        self,
        *,
        camera: CameraOrAll | MISSING = MISSING,
        format: Literal["json"] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Get the configured presets with position data measured in degrees.

        The reply format is not documented; with ``format=json`` it is JSON. Both are returned as text.

        Access: viewer.
        """
        return self._run(OPS.get_preset_data, None, {"camera": camera, "format": format}, request_options)

    def list_auxiliary_commands(
        self,
        *,
        camera: Camera | MISSING = MISSING,
        format: Literal["json"] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """List the supported auxiliary commands (product and release dependent).

        The reply format is not documented; with ``format=json`` it is JSON. Both are returned as text.

        Access: viewer.
        """
        return self._run(OPS.list_auxiliary_commands, None, {"camera": camera, "format": format}, request_options)

    def get_attributes(
        self,
        *,
        camera: CameraOrAll | MISSING = MISSING,
        format: Literal["json"] | MISSING = MISSING,
        group: Literal["zoom", "focus", "speed", "speeddry"] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Get PTZ attributes such as zoom, focus and speed steps (product and release dependent).

        Plain text has a section ``Attributes for camera <n>`` per channel with ``<attribute>=<entries>``
        lines whose array entries are comma separated and whose keys and values are joined by ``|``. With
        ``format=json`` the reply is a JSON object keyed by ``Camera <n>``. Both are returned as text. The
        attributes are speeds, minFocus, maxOpticalZoomMag, maxDigitalZoomMag, zoomSteps and isOverview.

        Access: viewer.
        """
        return self._run(
            OPS.get_attributes, None, {"camera": camera, "format": format, "group": group}, request_options
        )

    def get_info(self, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None) -> str:
        """Describe the available PTZ commands of a video channel. Access: viewer."""
        return self._run(OPS.get_info, None, {"camera": camera}, request_options)

    def get_driver_name(
        self, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> str:
        """Get the name of the system-configured device driver. Access: viewer."""
        return self._run(OPS.get_driver_name, None, {"camera": camera}, request_options)

    def set_server_preset_name(
        self,
        name: PresetName,
        *,
        home: Literal["yes"] | MISSING = MISSING,
        camera: Camera | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Save the current position as a named server preset.

        A preset saved with a name also gets a number, and the name and number commands can be used on the
        same preset.

        Access: admin.
        """
        self._run(OPS.set_server_preset_name, None, {"name": name, "home": home, "camera": camera}, request_options)

    def set_server_preset_number(
        self,
        number: int,
        *,
        home: Literal["yes"] | MISSING = MISSING,
        camera: Camera | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Save the current position as a numbered server preset. Access: admin."""
        self._run(
            OPS.set_server_preset_number, None, {"number": number, "home": home, "camera": camera}, request_options
        )

    def rename_server_preset(
        self,
        number: int,
        new_name: PresetName,
        *,
        camera: Camera | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Rename a server preset. Changes only the fields given. Access: admin."""
        self._run(
            OPS.rename_server_preset, None, {"number": number, "new_name": new_name, "camera": camera}, request_options
        )

    def remove_server_preset_name(
        self, name: PresetName, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Remove the server preset with a name.

        When the home preset is removed a new default home preset is created before the request is answered.

        Access: admin.
        """
        self._run(OPS.remove_server_preset_name, None, {"name": name, "camera": camera}, request_options)

    def remove_server_preset_number(
        self, number: int, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Remove the server preset with a number.

        When the home preset is removed a new default home preset is created before the request is answered.

        Access: admin.
        """
        self._run(OPS.remove_server_preset_number, None, {"number": number, "camera": camera}, request_options)

    def remove_all_server_presets(
        self, *, camera: CameraOrAll | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Remove all server presets of a video channel, or of every channel.

        With ``camera="all"`` the presets are removed from all active PTZ channels.

        Access: admin.
        """
        self._run(OPS.remove_all_server_presets, None, {"camera": camera}, request_options)

    def set_device_preset(
        self, preset: int, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Save the current position as a preset directly in the device, bypassing the preset interface.

        The preset position number is device specific and may also be a device specific special function.

        Access: admin.
        """
        self._run(OPS.set_device_preset, None, {"preset": preset, "camera": camera}, request_options)

    def control_osd_menu(
        self,
        command: Literal["open", "close", "up", "down", "left", "right", "select", "back"],
        *,
        camera: Camera | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Control the OSD menu of the external device.

        Which commands are supported, and how they behave, is driver dependent.

        Access: admin.
        """
        self._run(OPS.control_osd_menu, None, {"command": command, "camera": camera}, request_options)


class AsyncPtzControlApi(AsyncApi):
    """PTZ control API (``ptz-control``)."""

    INFO = INFO

    async def move(
        self,
        move: Literal["home", "up", "down", "left", "right", "upleft", "upright", "downleft", "downright", "stop"],
        *,
        camera: Camera | MISSING = MISSING,
        speed: Speed | MISSING = MISSING,
        imagerotation: ImageRotation | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Move the image or the device in a direction, go to the home position or stop the pan and tilt movement.

        On absolute (digital) PTZ the image moves 25 % of the image field width in the direction; on
        relative PTZ the device moves roughly 50 to 90 degrees (driver specific). ``home`` moves to the home
        position and ``stop`` stops the pan and tilt movement.

        Access: viewer.
        """
        await self._run(
            OPS.move,
            None,
            {"move": move, "camera": camera, "speed": speed, "imagerotation": imagerotation},
            request_options,
        )

    @overload
    async def center(self, request: CenterRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    async def center(
        self,
        center: list[int],
        /,
        *,
        imagewidth: int | MISSING = MISSING,
        imageheight: int | MISSING = MISSING,
        camera: Camera | MISSING = MISSING,
        imagerotation: ImageRotation | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def center(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Center the camera on pixel coordinates of the client video stream. Access: viewer."""
        if request is MISSING:
            request = None
        elif args or not isinstance(request, CenterRequest):
            kwargs = bind_positional(OPS.center, ("center",), (request, *args), kwargs)
            request = None
        await self._run(OPS.center, request, kwargs, request_options)

    @overload
    async def area_zoom(
        self, request: AreaZoomRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def area_zoom(
        self,
        area: list[int],
        /,
        *,
        imagewidth: int | MISSING = MISSING,
        imageheight: int | MISSING = MISSING,
        camera: Camera | MISSING = MISSING,
        imagerotation: ImageRotation | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def area_zoom(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Center on pixel coordinates and zoom by a factor of z/100.

        A z above 100 zooms in (300 zooms in to a third of the current field of view); a z below 100 zooms
        out (50 zooms out to twice the field of view). On some products the precision improves when the lens
        offset parameters are calibrated.

        Access: viewer.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, AreaZoomRequest):
            kwargs = bind_positional(OPS.area_zoom, ("area",), (request, *args), kwargs)
            request = None
        await self._run(OPS.area_zoom, request, kwargs, request_options)

    @overload
    async def absolute_move(
        self, request: AbsoluteMoveRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def absolute_move(
        self,
        /,
        *,
        pan: float | MISSING = MISSING,
        tilt: float | MISSING = MISSING,
        zoom: int | MISSING = MISSING,
        focus: int | MISSING = MISSING,
        iris: int | MISSING = MISSING,
        brightness: int | MISSING = MISSING,
        speed: Speed | MISSING = MISSING,
        camera: Camera | MISSING = MISSING,
        imagerotation: ImageRotation | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def absolute_move(
        self,
        request: AbsoluteMoveRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Move pan, tilt, zoom, focus, iris and brightness to absolute positions.

        Several axes can be combined in one request. Float input to zoom, focus, iris and brightness is
        handled as an integer, with no guarantee on the rounding. On Panopsis products a position where the
        fisheye lens is visible switches the product to overview mode.

        Access: viewer.
        """
        await self._run(OPS.absolute_move, request, kwargs, request_options)

    @overload
    async def relative_move(
        self, request: RelativeMoveRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def relative_move(
        self,
        /,
        *,
        rpan: float | MISSING = MISSING,
        rtilt: float | MISSING = MISSING,
        rzoom: int | MISSING = MISSING,
        rfocus: int | MISSING = MISSING,
        riris: int | MISSING = MISSING,
        rbrightness: int | MISSING = MISSING,
        speed: Speed | MISSING = MISSING,
        camera: Camera | MISSING = MISSING,
        imagerotation: ImageRotation | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def relative_move(
        self,
        request: RelativeMoveRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Move pan, tilt, zoom, focus, iris and brightness relative to the current position.

        Several axes can be combined in one request. Positive rzoom zooms in, positive rfocus focuses far,
        positive riris opens the iris and positive rbrightness gives a brighter image. On Panopsis products
        the command has no effect in overview mode.

        Access: viewer.
        """
        await self._run(OPS.relative_move, request, kwargs, request_options)

    @overload
    async def continuous_move(
        self, request: ContinuousMoveRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def continuous_move(
        self,
        /,
        *,
        pan_tilt: list[Annotated[int, Field(ge=-100, le=100)]] | MISSING = MISSING,
        zoom: int | MISSING = MISSING,
        focus: int | MISSING = MISSING,
        iris: int | MISSING = MISSING,
        brightness: int | MISSING = MISSING,
        proportionalspeed: Literal["disabled"] | MISSING = MISSING,
        camera: Camera | MISSING = MISSING,
        imagerotation: ImageRotation | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def continuous_move(
        self,
        request: ContinuousMoveRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Start a continuous pan, tilt, zoom, focus, iris or brightness movement; 0 stops it.

        Speeds range from -100 to 100. Positive pan is right, positive tilt is up, positive zoom zooms in,
        positive focus focuses far, positive iris opens the iris and positive brightness gives a brighter
        image. On Panopsis products the zoom, focus, iris and brightness moves have no effect in overview
        mode.

        Access: viewer.
        """
        await self._run(OPS.continuous_move, request, kwargs, request_options)

    async def set_autofocus(
        self, autofocus: OnOff, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable auto focus. Changes only the fields given. Access: viewer."""
        await self._run(OPS.set_autofocus, None, {"autofocus": autofocus, "camera": camera}, request_options)

    async def set_autoiris(
        self, autoiris: OnOff, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Enable or disable auto iris. Changes only the fields given. Access: viewer."""
        await self._run(OPS.set_autoiris, None, {"autoiris": autoiris, "camera": camera}, request_options)

    async def set_ir_cut_filter(
        self,
        ircutfilter: Literal["auto", "on", "off"],
        *,
        camera: Camera | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Control the IR cut filter.

        ``on`` applies the filter and blocks IR light, ``off`` removes it and lets IR light reach the
        sensor, ``auto`` switches depending on the lighting conditions (product and release dependent).

        Changes only the fields given. Access: viewer.
        """
        await self._run(OPS.set_ir_cut_filter, None, {"ircutfilter": ircutfilter, "camera": camera}, request_options)

    async def set_backlight(
        self, backlight: OnOff, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Control the backlight compensation.

        ``on`` is bright mode and ``off`` normal mode.

        Changes only the fields given. Access: viewer.
        """
        await self._run(OPS.set_backlight, None, {"backlight": backlight, "camera": camera}, request_options)

    async def activate_auxiliary(
        self, function: str, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Activate or deactivate a device specific auxiliary function.

        The function names are driver specific; see ``list_auxiliary_commands`` or ``get_info``.

        Access: viewer.
        """
        await self._run(OPS.activate_auxiliary, None, {"function": function, "camera": camera}, request_options)

    async def go_to_server_preset_name(
        self,
        name: str,
        *,
        camera: Camera | MISSING = MISSING,
        speed: Speed | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Move to the server preset with a name. Access: viewer."""
        await self._run(
            OPS.go_to_server_preset_name, None, {"name": name, "camera": camera, "speed": speed}, request_options
        )

    async def go_to_server_preset_number(
        self,
        number: int,
        *,
        camera: Camera | MISSING = MISSING,
        speed: Speed | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Move to the server preset with a number. Access: viewer."""
        await self._run(
            OPS.go_to_server_preset_number, None, {"number": number, "camera": camera, "speed": speed}, request_options
        )

    async def go_to_device_preset(
        self,
        preset: int,
        *,
        camera: Camera | MISSING = MISSING,
        speed: Speed | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Move to a preset stored in the device, bypassing the preset interface of the product.

        The preset position number is device specific and may also be a device specific special function.

        Access: viewer.
        """
        await self._run(
            OPS.go_to_device_preset, None, {"preset": preset, "camera": camera, "speed": speed}, request_options
        )

    async def get_limits(
        self, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> PtzLimits:
        """Get the PTZ limits of the product. Access: viewer."""
        return await self._run(OPS.get_limits, None, {"camera": camera}, request_options)

    async def get_mode(
        self, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> str:
        """Get the current mode (overview or normal) of a product with Panopsis technology.

        Access: viewer.
        """
        return await self._run(OPS.get_mode, None, {"camera": camera}, request_options)

    async def get_position(
        self, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> PtzPosition:
        """Get the current PTZ position (driver specific). Access: viewer."""
        return await self._run(OPS.get_position, None, {"camera": camera}, request_options)

    async def get_speed(
        self, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> PtzSpeed:
        """Get the pan and tilt speed. Access: viewer."""
        return await self._run(OPS.get_speed, None, {"camera": camera}, request_options)

    async def list_presets(
        self,
        *,
        camera: CameraOrAll | MISSING = MISSING,
        format: Literal["json"] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """List the preset positions of a video channel.

        The text reply is ``Preset Positions for camera <n>`` followed by ``presetposno<n>=<name>`` lines,
        encoded as set by ``PTZ.ResponseEncoding``. With ``format=json`` the reply is JSON; both are
        returned as text.

        Access: viewer.
        """
        return await self._run(OPS.list_presets, None, {"camera": camera, "format": format}, request_options)

    async def list_all_presets(
        self, *, format: Literal["json"] | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> str:
        """List the preset positions of all video channels.

        Plain text in the same form as ``list_presets``, one section per channel. With ``format=json`` the
        reply is JSON.

        Access: viewer.
        """
        return await self._run(OPS.list_all_presets, None, {"format": format}, request_options)

    async def get_preset_data(
        self,
        *,
        camera: CameraOrAll | MISSING = MISSING,
        format: Literal["json"] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Get the configured presets with position data measured in degrees.

        The reply format is not documented; with ``format=json`` it is JSON. Both are returned as text.

        Access: viewer.
        """
        return await self._run(OPS.get_preset_data, None, {"camera": camera, "format": format}, request_options)

    async def list_auxiliary_commands(
        self,
        *,
        camera: Camera | MISSING = MISSING,
        format: Literal["json"] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """List the supported auxiliary commands (product and release dependent).

        The reply format is not documented; with ``format=json`` it is JSON. Both are returned as text.

        Access: viewer.
        """
        return await self._run(OPS.list_auxiliary_commands, None, {"camera": camera, "format": format}, request_options)

    async def get_attributes(
        self,
        *,
        camera: CameraOrAll | MISSING = MISSING,
        format: Literal["json"] | MISSING = MISSING,
        group: Literal["zoom", "focus", "speed", "speeddry"] | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> str:
        """Get PTZ attributes such as zoom, focus and speed steps (product and release dependent).

        Plain text has a section ``Attributes for camera <n>`` per channel with ``<attribute>=<entries>``
        lines whose array entries are comma separated and whose keys and values are joined by ``|``. With
        ``format=json`` the reply is a JSON object keyed by ``Camera <n>``. Both are returned as text. The
        attributes are speeds, minFocus, maxOpticalZoomMag, maxDigitalZoomMag, zoomSteps and isOverview.

        Access: viewer.
        """
        return await self._run(
            OPS.get_attributes, None, {"camera": camera, "format": format, "group": group}, request_options
        )

    async def get_info(
        self, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> str:
        """Describe the available PTZ commands of a video channel. Access: viewer."""
        return await self._run(OPS.get_info, None, {"camera": camera}, request_options)

    async def get_driver_name(
        self, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> str:
        """Get the name of the system-configured device driver. Access: viewer."""
        return await self._run(OPS.get_driver_name, None, {"camera": camera}, request_options)

    async def set_server_preset_name(
        self,
        name: PresetName,
        *,
        home: Literal["yes"] | MISSING = MISSING,
        camera: Camera | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Save the current position as a named server preset.

        A preset saved with a name also gets a number, and the name and number commands can be used on the
        same preset.

        Access: admin.
        """
        await self._run(
            OPS.set_server_preset_name, None, {"name": name, "home": home, "camera": camera}, request_options
        )

    async def set_server_preset_number(
        self,
        number: int,
        *,
        home: Literal["yes"] | MISSING = MISSING,
        camera: Camera | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Save the current position as a numbered server preset. Access: admin."""
        await self._run(
            OPS.set_server_preset_number, None, {"number": number, "home": home, "camera": camera}, request_options
        )

    async def rename_server_preset(
        self,
        number: int,
        new_name: PresetName,
        *,
        camera: Camera | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Rename a server preset. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.rename_server_preset, None, {"number": number, "new_name": new_name, "camera": camera}, request_options
        )

    async def remove_server_preset_name(
        self, name: PresetName, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Remove the server preset with a name.

        When the home preset is removed a new default home preset is created before the request is answered.

        Access: admin.
        """
        await self._run(OPS.remove_server_preset_name, None, {"name": name, "camera": camera}, request_options)

    async def remove_server_preset_number(
        self, number: int, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Remove the server preset with a number.

        When the home preset is removed a new default home preset is created before the request is answered.

        Access: admin.
        """
        await self._run(OPS.remove_server_preset_number, None, {"number": number, "camera": camera}, request_options)

    async def remove_all_server_presets(
        self, *, camera: CameraOrAll | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Remove all server presets of a video channel, or of every channel.

        With ``camera="all"`` the presets are removed from all active PTZ channels.

        Access: admin.
        """
        await self._run(OPS.remove_all_server_presets, None, {"camera": camera}, request_options)

    async def set_device_preset(
        self, preset: int, *, camera: Camera | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Save the current position as a preset directly in the device, bypassing the preset interface.

        The preset position number is device specific and may also be a device specific special function.

        Access: admin.
        """
        await self._run(OPS.set_device_preset, None, {"preset": preset, "camera": camera}, request_options)

    async def control_osd_menu(
        self,
        command: Literal["open", "close", "up", "down", "left", "right", "select", "back"],
        *,
        camera: Camera | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Control the OSD menu of the external device.

        Which commands are supported, and how they behave, is driver dependent.

        Access: admin.
        """
        await self._run(OPS.control_osd_menu, None, {"command": command, "camera": camera}, request_options)
