# GENERATED from specs/apis/applications/license-plate-verifier.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""AXIS License Plate Verifier (ALPV, /local/fflprapp/): integration settings, ALPV settings, list management, event search and statistics.

Docs: https://developer.axis.com/vapix/applications/license-plate-verifier-api/
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Annotated, Any, ClassVar, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import CONST, AcapDiscovery, ApiInfo, Family, Model, Operation
from .._protocols.cgi import CgiArg, CgiBinding, JsonReply, Text, Xml
from .._protocols.xmlmap import XmlField, XmlMap
from ._base import AsyncApi, SyncApi, bind_positional

# ---------------------------------------------------------------------------
# Models


class TwoNConfig(Model):
    """2N integration settings (<tn_config> XML)."""

    __masked__: ClassVar[frozenset[str]] = frozenset({"password"})
    url: str | None = None
    """The 2N device URL."""
    user: str | None = None
    password: str | None = None
    """Base64 in sample."""
    enable: bool | None = None
    """Enable or disable ALPV integration."""
    https: bool | None = None
    """Secure integration connection via HTTPS."""
    access_point: int | None = Field(default=None, validation_alias="accessPoint", serialization_alias="accessPoint")
    """Entry = 0, Exit = 1."""
    event_on_direction: int | None = None
    """Any = 0, In = 2, Out = 3."""


class GenetecConfig(Model):
    """Genetec integration settings (<gsc_config> XML)."""

    __masked__: ClassVar[frozenset[str]] = frozenset({"password"})
    url: str | None = None
    user: str | None = None
    password: str | None = None
    enable: bool | None = None
    https: bool | None = None
    """Present in get response only."""
    camera_id: str | None = Field(default=None, validation_alias="cameraID", serialization_alias="cameraID")


class Schedule(Model):
    enabled: bool | None = None
    start_time: str | None = None
    """Start time, in seconds."""
    end_time: str | None = None
    """End time, in seconds."""
    mon: bool | None = Field(default=None, validation_alias="Mon", serialization_alias="Mon")
    """The schedule applies on this day."""
    tue: bool | None = Field(default=None, validation_alias="Tue", serialization_alias="Tue")
    """The schedule applies on this day."""
    wed: bool | None = Field(default=None, validation_alias="Wed", serialization_alias="Wed")
    """The schedule applies on this day."""
    thu: bool | None = Field(default=None, validation_alias="Thu", serialization_alias="Thu")
    """The schedule applies on this day."""
    fri: bool | None = Field(default=None, validation_alias="Fri", serialization_alias="Fri")
    """The schedule applies on this day."""
    sat: bool | None = Field(default=None, validation_alias="Sat", serialization_alias="Sat")
    """The schedule applies on this day."""
    sun: bool | None = Field(default=None, validation_alias="Sun", serialization_alias="Sun")
    """The schedule applies on this day."""


ListMode = Literal["allow", "block", "none"]


class PlateList(Model):
    id: str
    """The list ID string."""
    name: str
    """The list name; change it to rename the list."""
    schedule: list[Schedule] | None = None
    mode: ListMode | None = None
    """The list mode."""


class ListSettings(Model):
    lists: list[PlateList]


ListName = Literal["allow", "block", "custom"]


class RecognitionEvent(Model):
    """One recognition record. The docs give only a sample, no field table; the meanings below come from the sample and the event-search filters."""

    ts: str | None = Field(default=None, validation_alias="TS", serialization_alias="TS")
    """Record kind, CAR in the sample."""
    mod_ts: str | None = Field(default=None, validation_alias="MOD_TS", serialization_alias="MOD_TS")
    """Modification time as local text, for example 2023-12-12 16:12:04 EET."""
    end_ts: str | None = Field(default=None, validation_alias="END_TS", serialization_alias="END_TS")
    car_id: int | None = Field(default=None, validation_alias="CAR_ID", serialization_alias="CAR_ID")
    """Internal runtime plate id."""
    lpr: str | None = Field(default=None, validation_alias="LPR", serialization_alias="LPR")
    """Plate text."""
    lpr_utf8: str | None = Field(default=None, validation_alias="LPR_UTF8", serialization_alias="LPR_UTF8")
    lpr_unicode: str | None = Field(default=None, validation_alias="LPR_UNICODE", serialization_alias="LPR_UNICODE")
    rtime: float | None = Field(default=None, validation_alias="RTIME", serialization_alias="RTIME")
    """Recognition time."""
    action: int | None = Field(default=None, validation_alias="ACTION", serialization_alias="ACTION")
    act_param: str | None = Field(default=None, validation_alias="ACT_PARAM", serialization_alias="ACT_PARAM")
    """List name for list matches."""
    threshold: float | None = Field(default=None, validation_alias="THRESHOLD", serialization_alias="THRESHOLD")
    roi_x: int | None = Field(default=None, validation_alias="ROI_X", serialization_alias="ROI_X")
    roi_y: int | None = Field(default=None, validation_alias="ROI_Y", serialization_alias="ROI_Y")
    roi_w: int | None = Field(default=None, validation_alias="ROI_W", serialization_alias="ROI_W")
    roi_h: int | None = Field(default=None, validation_alias="ROI_H", serialization_alias="ROI_H")
    lp_x: int | None = Field(default=None, validation_alias="LP_X", serialization_alias="LP_X")
    lp_y: int | None = Field(default=None, validation_alias="LP_Y", serialization_alias="LP_Y")
    lp_w: int | None = Field(default=None, validation_alias="LP_W", serialization_alias="LP_W")
    lp_h: int | None = Field(default=None, validation_alias="LP_H", serialization_alias="LP_H")
    roi_id: int | None = Field(default=None, validation_alias="ROI_ID", serialization_alias="ROI_ID")
    roi_idu: int | None = Field(default=None, validation_alias="ROI_IDU", serialization_alias="ROI_IDU")
    frames: int | None = Field(default=None, validation_alias="FRAMES", serialization_alias="FRAMES")
    direction: int | None = Field(default=None, validation_alias="DIRECTION", serialization_alias="DIRECTION")
    lp_bmp: str | None = Field(default=None, validation_alias="LP_BMP", serialization_alias="LP_BMP")
    """Relative URL of the plate image (tools.cgi?action=getImage&name=...)."""
    roi_bmp: str | None = Field(default=None, validation_alias="ROI_BMP", serialization_alias="ROI_BMP")
    """Relative URL of the area-of-interest image."""
    country: str | None = Field(default=None, validation_alias="COUNTRY", serialization_alias="COUNTRY")
    lp_list_mode: int | None = Field(default=None, validation_alias="LP_LIST_MODE", serialization_alias="LP_LIST_MODE")
    lp_description: str | None = Field(
        default=None, validation_alias="LP_DESCRIPTION", serialization_alias="LP_DESCRIPTION"
    )
    """Plate description from the list the plate is on."""
    lp_region_utf8: str | None = Field(
        default=None, validation_alias="LP_REGION_UTF8", serialization_alias="LP_REGION_UTF8"
    )
    iso3166_2_code: str | None = Field(
        default=None, validation_alias="ISO3166_2_CODE", serialization_alias="ISO3166_2_CODE"
    )
    lp_type: int | None = Field(default=None, validation_alias="LP_TYPE", serialization_alias="LP_TYPE")
    ext1: str | None = Field(default=None, validation_alias="EXT1", serialization_alias="EXT1")
    ext2: str | None = Field(default=None, validation_alias="EXT2", serialization_alias="EXT2")
    ext3: str | None = Field(default=None, validation_alias="EXT3", serialization_alias="EXT3")
    car_m_type: str | None = Field(default=None, validation_alias="CAR_M_TYPE", serialization_alias="CAR_M_TYPE")
    """Vehicle type, CAR in the sample."""
    car_color: str | None = Field(default=None, validation_alias="CAR_COLOR", serialization_alias="CAR_COLOR")
    car_conf: float | None = Field(default=None, validation_alias="CAR_CONF", serialization_alias="CAR_CONF")
    car_view: int | None = Field(default=None, validation_alias="CAR_VIEW", serialization_alias="CAR_VIEW")
    """0 = front, 1 = rear."""


class EventSearchResult(Model):
    current_timestamp_us: int | None = Field(
        default=None, validation_alias="currentTimestampUs", serialization_alias="currentTimestampUs"
    )
    """Current device time in microseconds."""
    events: list[RecognitionEvent] | None = Field(default=None, validation_alias="event", serialization_alias="event")


class DirectionCounts(Model):
    in_: int | None = Field(default=None, validation_alias="in", serialization_alias="in")
    out: int | None = None
    unknown: int | None = Field(default=None, validation_alias="unk", serialization_alias="unk")


class ListCounts(Model):
    blocklist: int | None = None
    allowlist: int | None = None
    customlist: int | None = None
    nonelist: int | None = None


class RoiCounts(Model):
    roi1: int | None = None
    roi2: int | None = None


class VehicleCounts(Model):
    direction: DirectionCounts | None = None
    lists: ListCounts | None = Field(default=None, validation_alias="list", serialization_alias="list")
    roi: RoiCounts | None = None
    total: int | None = None


class Statistics(Model):
    current_timestamp_us: int | None = Field(
        default=None, validation_alias="currentTimestampUs", serialization_alias="currentTimestampUs"
    )
    """Current device time in microseconds."""
    counts: VehicleCounts | None = Field(default=None, validation_alias="vcount", serialization_alias="vcount")


class PushConfig(Model):
    """One push profile (<cloud_config> XML)."""

    __masked__: ClassVar[frozenset[str]] = frozenset({"password", "x_auth_key"})
    url: str | None = None
    """The target URL, base64 encoded, as <servername>:port/path. No path is present when TCP is used."""
    latitude: float | None = None
    """The camera latitude."""
    longitude: float | None = None
    """The camera longitude."""
    sensor_provider_id: str | None = Field(
        default=None, validation_alias="sensorProviderID", serialization_alias="sensorProviderID"
    )
    """The camera identifier sent with all requests, to tell cameras apart."""
    protocol: Literal[1, 8, 16] | None = None
    """The protocol: HTTP = 1, TCP = 8, FTP = 16."""
    enable: bool | None = None
    skip_image_in_post: bool | None = None
    """True sends the JSON packet without images."""
    event_new: bool | None = None
    """Send NEW events."""
    event_update: bool | None = None
    """Send UPDATE events."""
    event_lost: bool | None = None
    """Send LOST events."""
    use_multipart: bool | None = None
    """True sends multipart/form-data, false sends application/json."""
    use_event_buffer: bool | None = None
    """Re-send events from a buffer if the target URL is not accessible."""
    user: str | None = None
    password: str | None = None
    http_auth_type: int | None = None
    """Undocumented."""
    send_second_image: bool | None = None
    """Send a second image of the license plate type."""
    second_image_type: int | None = None
    """Undocumented."""
    path_template: str | None = None
    """The custom path for FTP."""
    x_auth_key: str | None = None
    """The Auth-Header."""


PushProfile = Literal["cloud", "cloud2", "cloud3"]
ListFile = Literal["allow_list", "block_list", "custom_list"]


class PlateListContent(Model):
    """A list as returned by its CGI (<bw_list mode="..."> XML)."""

    mode: str | None = None
    """The list mode (allow, block or custom)."""
    plates: list[str] | None = None
    """The entries, as 'PLATE,MM-DD-YYYY,description'."""


class HeartbeatDataSystem(Model):
    timestamp: bool | None = None


class HeartbeatDataIdentify(Model):
    platform: bool | None = None
    version: bool | None = None
    ip_address: bool | None = Field(default=None, validation_alias="ipAddress", serialization_alias="ipAddress")
    mac_address: bool | None = Field(default=None, validation_alias="macAddress", serialization_alias="macAddress")
    os_version: bool | None = Field(default=None, validation_alias="osVersion", serialization_alias="osVersion")
    anpr_version: bool | None = Field(default=None, validation_alias="anprVersion", serialization_alias="anprVersion")


class HeartbeatDataAlpv(Model):
    version: bool | None = None
    device_id: bool | None = Field(default=None, validation_alias="device_ID", serialization_alias="device_ID")
    num_frames: bool | None = Field(default=None, validation_alias="numFrames", serialization_alias="numFrames")
    num_frames_avg: bool | None = Field(
        default=None, validation_alias="numFramesAvg", serialization_alias="numFramesAvg"
    )
    numberof_reads: bool | None = Field(
        default=None, validation_alias="numberofReads", serialization_alias="numberofReads"
    )


class HeartbeatDataServices(Model):
    available_memory: bool | None = Field(
        default=None, validation_alias="Available Memory", serialization_alias="Available Memory"
    )


class HeartbeatData(Model):
    """Which fields the heartbeat message includes. Sections are objects of booleans."""

    system: HeartbeatDataSystem | None = None
    identify: HeartbeatDataIdentify | None = None
    alpv: HeartbeatDataAlpv | None = Field(default=None, validation_alias="ALPV", serialization_alias="ALPV")
    services: HeartbeatDataServices | None = None


class DirectionRoi(Model):
    id: int
    name: str
    """For example roi1."""
    type: str
    """For example polygon."""
    active: bool
    angle: int = Field(ge=0, le=360000)
    """The car direction angle, documented as <0-360000> (unit not stated)."""
    coordinates: list[Annotated[list[int], Field(min_length=2, max_length=2)]]
    """Corner points [x, y]."""


class DirectionConfig(Model):
    """The body of config_json.cgi for changing the ROI direction angle."""

    api: Annotated[Literal["setconfig"], CONST]
    """Default: 'setconfig'."""
    config: Annotated[Literal["roi"], CONST]
    """Default: 'roi'."""
    roi: list[DirectionRoi]


class AddPlateRequest(Model):
    plate: str
    """Plate text with date and description: <plate text>,<plate date>,<description>, for example AA12DD,12-12-2023,Plate_description."""
    list: ListName


class DeletePlateRequest(Model):
    plate: str
    """The plate text that should be deleted."""
    list: ListName


class UploadListRequest(Model):
    command: Literal["new", "upload", "save"]
    list: str
    """Documented as '<file name>.csv' in the step examples; the shell script passes the list name (block or allow)."""
    data: str | None = None
    """For command=upload: a CSV chunk (the shell example sends 500 lines per chunk)."""


class SearchEventsRequest(Model):
    timestampfrom: int | None = None
    """Only records from this time. Documented as milliseconds; the example 1702386728835000 looks like microseconds. Can be used without timestampto."""
    timestampto: int | None = None
    """Only records up to this time. Can be used without timestampfrom."""
    text: str | None = None
    """The plate text."""
    place_desc: str | None = Field(default=None, validation_alias="place desc", serialization_alias="place desc")
    """Plate description from list management. The exact query key is unclear."""
    country: str | None = None
    """Country in ISO 3166 alpha-3 format, for example CZE."""
    car_type: Literal[1, 2, 32] | None = None
    """CAR = 1, BUS = 2, TRUCK = 32."""
    car_color: Literal[65536, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10] | None = None
    """65536 = any or undefined, 0 Beige, 1 Black, 2 Blue, 3 Brown, 4 Gray, 5 Green, 6 Orange, 7 Red, 8 White, 9 Yellow, 10 Silver."""
    roi_id: int | None = None
    """Area of interest id; -1 in the example. Undocumented."""
    car_direction: int | None = None
    """-1 for any."""
    car_view: Literal[0, 1] | None = None
    """Front = 0, rear = 1."""
    action: Literal[0, 1] | None = None
    """Filter on whether an action was taken: 1 = opened, 0 = no action."""
    offset: int | None = None
    """Number of records to skip, like SQL OFFSET."""
    limit: int | None = None
    """Limit the number of result records."""


class GetStatisticsRequest(Model):
    limit: int | None = None
    """The example uses limit=0 to get statistics only."""


class Set2nConfigRequest(Model):
    config: str
    """The <tn_config> XML document (url, user, password, enable, https, accessPoint, event_on_direction)."""


class SetGenetecConfigRequest(Model):
    config: str
    """The <gsc_config> XML document (url, user, password, enable, cameraID)."""


class SetSettingsRequest(Model):
    configuration: str
    """The <configuration> XML document."""


class GetPushConfigRequest(Model):
    profile: PushProfile


class SetPushConfigRequest(Model):
    profile: PushProfile
    config: str
    """The <cloud_config> XML document."""


class SetHeartbeatConfigRequest(Model):
    config: str
    """The <hb_config> XML document: url (base64), user, password (base64), period (5, 10, 30, 60 or 1440 minutes), enable, x_auth_key, http_auth_type."""


class SetHeartbeatDataRequest(Model):
    data: HeartbeatData


class SetDirectionRequest(Model):
    config: DirectionConfig


class SetListSettingsRequest(Model):
    settings: ListSettings


class GetListRequest(Model):
    list_file: ListFile


class AddPlatesRequest(Model):
    list_file: ListFile
    plates: str
    """The <bw_list mode="allow|block|custom"> XML document with one <s> element per plate."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/local/fflprapp/api.cgi"

INFO = ApiInfo(
    id="license-plate-verifier",
    name="License plate verifier API",
    family=Family.CGI,
    discovery=(AcapDiscovery("fflprapp"),),
    docs=("https://developer.axis.com/vapix/applications/license-plate-verifier-api/",),
)


class OPS:
    get_2n_config = Operation(
        INFO,
        "get_2n_config",
        CgiBinding(
            "/local/fflprapp/config_2n.cgi",
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField("url", source="child"),
                        XmlField("user", source="child"),
                        XmlField("password", source="child"),
                        XmlField("enable", source="child"),
                        XmlField("https", source="child"),
                        XmlField("accessPoint", source="child"),
                        XmlField("event_on_direction", source="child"),
                    ),
                    root=".",
                )
            ),
        ),
        result=TwoNConfig,
        access="admin",
        effect="read",
    )
    get_genetec_config = Operation(
        INFO,
        "get_genetec_config",
        CgiBinding(
            "/local/fflprapp/config_gsc.cgi",
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField("url", source="child"),
                        XmlField("user", source="child"),
                        XmlField("password", source="child"),
                        XmlField("enable", source="child"),
                        XmlField("https", source="child"),
                        XmlField("cameraID", source="child"),
                    ),
                    root=".",
                )
            ),
        ),
        result=GenetecConfig,
        access="admin",
        effect="read",
    )
    get_settings = Operation(
        INFO,
        "get_settings",
        CgiBinding("/local/fflprapp/config.cgi", reply=Xml()),
        result=ET.Element,
        access="admin",
        effect="read",
    )
    get_roi = Operation(
        INFO,
        "get_roi",
        CgiBinding(PATH, fixed_query=(("api", "getrroi"),), reply=Text()),
        result=str,
        access="admin",
        effect="read",
    )
    get_list_settings = Operation(
        INFO,
        "get_list_settings",
        CgiBinding("/local/fflprapp/list_mgmt.cgi", reply=JsonReply()),
        result=ListSettings,
        access="admin",
        effect="read",
    )
    add_plate = Operation(
        INFO,
        "add_plate",
        CgiBinding(PATH, fixed_query=(("api", "addplate"),), args=(CgiArg("plate"), CgiArg("list")), reply=Text()),
        params=AddPlateRequest,
        access="admin",
        effect="write",
        write="create",
    )
    delete_plate = Operation(
        INFO,
        "delete_plate",
        CgiBinding(PATH, fixed_query=(("api", "delplate"),), args=(CgiArg("plate"), CgiArg("list")), reply=Text()),
        params=DeletePlateRequest,
        access="admin",
        effect="write",
        write="delete",
    )
    export_allow_list = Operation(
        INFO,
        "export_allow_list",
        CgiBinding(PATH, fixed_query=(("api", "exportallow"),), reply=Text()),
        result=str,
        access="admin",
        effect="read",
    )
    export_block_list = Operation(
        INFO,
        "export_block_list",
        CgiBinding(PATH, fixed_query=(("api", "exportblock"),), reply=Text()),
        result=str,
        access="admin",
        effect="read",
    )
    export_custom_list = Operation(
        INFO,
        "export_custom_list",
        CgiBinding(PATH, fixed_query=(("api", "exportcustom"),), reply=Text()),
        result=str,
        access="admin",
        effect="read",
    )
    upload_list = Operation(
        INFO,
        "upload_list",
        CgiBinding(
            "/local/fflprapp/upload.cgi",
            method="POST",
            encoding="form",
            args=(CgiArg("command"), CgiArg("list"), CgiArg("data")),
            reply=Text(),
        ),
        params=UploadListRequest,
        access="admin",
        effect="write",
        write="create",
    )
    search_events = Operation(
        INFO,
        "search_events",
        CgiBinding(
            "/local/fflprapp/events.cgi",
            args=(
                CgiArg("timestampfrom"),
                CgiArg("timestampto"),
                CgiArg("text"),
                CgiArg("place_desc", wire="place desc"),
                CgiArg("country"),
                CgiArg("car_type"),
                CgiArg("car_color"),
                CgiArg("roi_id"),
                CgiArg("car_direction"),
                CgiArg("car_view"),
                CgiArg("action"),
                CgiArg("offset"),
                CgiArg("limit"),
            ),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField("currentTimestampUs", source="child"),
                        XmlField(
                            "event",
                            source="path",
                            many=True,
                            nested=XmlMap(
                                fields=(
                                    XmlField("TS", source="child"),
                                    XmlField("MOD_TS", source="child"),
                                    XmlField("END_TS", source="child"),
                                    XmlField("CAR_ID", source="child"),
                                    XmlField("LPR", source="child"),
                                    XmlField("LPR_UTF8", source="child"),
                                    XmlField("LPR_UNICODE", source="child"),
                                    XmlField("RTIME", source="child"),
                                    XmlField("ACTION", source="child"),
                                    XmlField("ACT_PARAM", source="child"),
                                    XmlField("THRESHOLD", source="child"),
                                    XmlField("ROI_X", source="child"),
                                    XmlField("ROI_Y", source="child"),
                                    XmlField("ROI_W", source="child"),
                                    XmlField("ROI_H", source="child"),
                                    XmlField("LP_X", source="child"),
                                    XmlField("LP_Y", source="child"),
                                    XmlField("LP_W", source="child"),
                                    XmlField("LP_H", source="child"),
                                    XmlField("ROI_ID", source="child"),
                                    XmlField("ROI_IDU", source="child"),
                                    XmlField("FRAMES", source="child"),
                                    XmlField("DIRECTION", source="child"),
                                    XmlField("LP_BMP", source="child"),
                                    XmlField("ROI_BMP", source="child"),
                                    XmlField("COUNTRY", source="child"),
                                    XmlField("LP_LIST_MODE", source="child"),
                                    XmlField("LP_DESCRIPTION", source="child"),
                                    XmlField("LP_REGION_UTF8", source="child"),
                                    XmlField("ISO3166_2_CODE", source="child"),
                                    XmlField("LP_TYPE", source="child"),
                                    XmlField("EXT1", source="child"),
                                    XmlField("EXT2", source="child"),
                                    XmlField("EXT3", source="child"),
                                    XmlField("CAR_M_TYPE", source="child"),
                                    XmlField("CAR_COLOR", source="child"),
                                    XmlField("CAR_CONF", source="child"),
                                    XmlField("CAR_VIEW", source="child"),
                                )
                            ),
                        ),
                    )
                )
            ),
        ),
        params=SearchEventsRequest,
        result=EventSearchResult,
        access="admin",
        effect="read",
    )
    get_statistics = Operation(
        INFO,
        "get_statistics",
        CgiBinding(
            "/local/fflprapp/search.cgi",
            args=(CgiArg("limit"),),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField("currentTimestampUs", source="child"),
                        XmlField(
                            "vcount",
                            source="path",
                            nested=XmlMap(
                                fields=(
                                    XmlField(
                                        "direction",
                                        source="path",
                                        nested=XmlMap(
                                            fields=(
                                                XmlField("in", source="child"),
                                                XmlField("out", source="child"),
                                                XmlField("unk", source="child"),
                                            )
                                        ),
                                    ),
                                    XmlField(
                                        "list",
                                        source="path",
                                        nested=XmlMap(
                                            fields=(
                                                XmlField("blocklist", source="child"),
                                                XmlField("allowlist", source="child"),
                                                XmlField("customlist", source="child"),
                                                XmlField("nonelist", source="child"),
                                            )
                                        ),
                                    ),
                                    XmlField(
                                        "roi",
                                        source="path",
                                        nested=XmlMap(
                                            fields=(XmlField("roi1", source="child"), XmlField("roi2", source="child"))
                                        ),
                                    ),
                                    XmlField("total", source="child"),
                                )
                            ),
                        ),
                    )
                )
            ),
        ),
        params=GetStatisticsRequest,
        result=Statistics,
        access="admin",
        effect="read",
    )
    set_2n_config = Operation(
        INFO,
        "set_2n_config",
        CgiBinding(
            "/local/fflprapp/config_2n.cgi",
            method="POST",
            encoding="body",
            content_type="application/xml",
            body_field="config",
            reply=Text(),
        ),
        params=Set2nConfigRequest,
        access="admin",
        effect="write",
        write="replace",
    )
    set_genetec_config = Operation(
        INFO,
        "set_genetec_config",
        CgiBinding(
            "/local/fflprapp/config_gsc.cgi",
            method="POST",
            encoding="body",
            content_type="application/xml",
            body_field="config",
            reply=Text(),
        ),
        params=SetGenetecConfigRequest,
        access="admin",
        effect="write",
        write="replace",
    )
    set_settings = Operation(
        INFO,
        "set_settings",
        CgiBinding(
            "/local/fflprapp/config.cgi",
            method="POST",
            encoding="body",
            content_type="application/xml",
            body_field="configuration",
            reply=Text(),
        ),
        params=SetSettingsRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_push_config = Operation(
        INFO,
        "get_push_config",
        CgiBinding(
            "/local/fflprapp/{profile}.cgi",
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField("url", source="child"),
                        XmlField("latitude", source="child"),
                        XmlField("longitude", source="child"),
                        XmlField("sensorProviderID", source="child"),
                        XmlField("protocol", source="child"),
                        XmlField("enable", source="child"),
                        XmlField("skip_image_in_post", source="child"),
                        XmlField("event_new", source="child"),
                        XmlField("event_update", source="child"),
                        XmlField("event_lost", source="child"),
                        XmlField("use_multipart", source="child"),
                        XmlField("use_event_buffer", source="child"),
                        XmlField("user", source="child"),
                        XmlField("password", source="child"),
                        XmlField("http_auth_type", source="child"),
                        XmlField("send_second_image", source="child"),
                        XmlField("second_image_type", source="child"),
                        XmlField("path_template", source="child"),
                        XmlField("x_auth_key", source="child"),
                    ),
                    root=".",
                )
            ),
        ),
        params=GetPushConfigRequest,
        result=PushConfig,
        access="admin",
        effect="read",
    )
    set_push_config = Operation(
        INFO,
        "set_push_config",
        CgiBinding(
            "/local/fflprapp/{profile}.cgi",
            method="POST",
            encoding="body",
            content_type="application/xml",
            body_field="config",
            reply=Text(),
        ),
        params=SetPushConfigRequest,
        access="admin",
        effect="write",
        write="replace",
    )
    set_heartbeat_config = Operation(
        INFO,
        "set_heartbeat_config",
        CgiBinding(
            "/local/fflprapp/config_hb.cgi",
            method="POST",
            encoding="body",
            content_type="application/xml",
            body_field="config",
            reply=Text(),
        ),
        params=SetHeartbeatConfigRequest,
        access="admin",
        effect="write",
        write="replace",
    )
    set_heartbeat_data = Operation(
        INFO,
        "set_heartbeat_data",
        CgiBinding(
            "/local/fflprapp/config_hb_data.cgi",
            method="POST",
            encoding="body",
            content_type="application/json",
            body_field="data",
            reply=Text(),
        ),
        params=SetHeartbeatDataRequest,
        access="admin",
        effect="write",
        write="replace",
    )
    set_direction = Operation(
        INFO,
        "set_direction",
        CgiBinding(
            "/local/fflprapp/config_json.cgi",
            method="POST",
            encoding="body",
            content_type="application/json",
            body_field="config",
            reply=Text(),
        ),
        params=SetDirectionRequest,
        access="admin",
        effect="write",
        write="replace",
    )
    set_list_settings = Operation(
        INFO,
        "set_list_settings",
        CgiBinding(
            "/local/fflprapp/list_mgmt.cgi",
            method="POST",
            encoding="body",
            content_type="application/json",
            body_field="settings",
            reply=Text(),
        ),
        params=SetListSettingsRequest,
        access="admin",
        effect="write",
        write="replace",
    )
    get_list = Operation(
        INFO,
        "get_list",
        CgiBinding(
            "/local/fflprapp/{list_file}.cgi",
            reply=Xml(
                map=XmlMap(fields=(XmlField("mode"), XmlField("plates", source="path", name="s", many=True)), root=".")
            ),
        ),
        params=GetListRequest,
        result=PlateListContent,
        access="admin",
        effect="read",
    )
    add_plates = Operation(
        INFO,
        "add_plates",
        CgiBinding(
            "/local/fflprapp/{list_file}.cgi",
            method="POST",
            encoding="body",
            content_type="application/xml",
            body_field="plates",
            reply=Text(),
        ),
        params=AddPlatesRequest,
        access="admin",
        effect="write",
        write="create",
    )


# ---------------------------------------------------------------------------
# API classes


class LicensePlateVerifierApi(SyncApi):
    """License plate verifier API (``license-plate-verifier``)."""

    INFO = INFO

    def get_2n_config(self, *, request_options: RequestOptions | None = None) -> TwoNConfig:
        """Get 2N integration settings. Access: admin."""
        return self._run(OPS.get_2n_config, None, {}, request_options)

    def get_genetec_config(self, *, request_options: RequestOptions | None = None) -> GenetecConfig:
        """Get Genetec integration settings. Access: admin."""
        return self._run(OPS.get_genetec_config, None, {}, request_options)

    def get_settings(self, *, request_options: RequestOptions | None = None) -> ET.Element:
        """Get the ALPV settings as the complete <configuration> XML element.

        The docs give a sample reply but no field table, so the result is the parsed XML root element.

        Access: admin.
        """
        return self._run(OPS.get_settings, None, {}, request_options)

    def get_roi(self, *, request_options: RequestOptions | None = None) -> str:
        """Get the Area of Interest configuration as text.

        The reply is a <pre> block listing the active ROI and its corner points.

        Access: admin.
        """
        return self._run(OPS.get_roi, None, {}, request_options)

    def get_list_settings(self, *, request_options: RequestOptions | None = None) -> ListSettings:
        """Get the list settings (allow, block and custom lists with schedules and modes).

        Access: admin.
        """
        return self._run(OPS.get_list_settings, None, {}, request_options)

    def add_plate(self, plate: str, list: ListName, *, request_options: RequestOptions | None = None) -> None:
        """Add a single plate to the allow, block or custom list. Access: admin."""
        self._run(OPS.add_plate, None, {"plate": plate, "list": list}, request_options)

    def delete_plate(self, plate: str, list: ListName, *, request_options: RequestOptions | None = None) -> None:
        """Remove a single plate from the allow, block or custom list. Access: admin."""
        self._run(OPS.delete_plate, None, {"plate": plate, "list": list}, request_options)

    def export_allow_list(self, *, request_options: RequestOptions | None = None) -> str:
        """Export the allow list as text lines 'PLATE,MM-DD-YYYY,description'. Access: admin."""
        return self._run(OPS.export_allow_list, None, {}, request_options)

    def export_block_list(self, *, request_options: RequestOptions | None = None) -> str:
        """Export the block list as text lines 'PLATE,MM-DD-YYYY,description'. Access: admin."""
        return self._run(OPS.export_block_list, None, {}, request_options)

    def export_custom_list(self, *, request_options: RequestOptions | None = None) -> str:
        """Export the custom list as text lines 'PLATE,MM-DD-YYYY,description'. Access: admin."""
        return self._run(OPS.export_custom_list, None, {}, request_options)

    def upload_list(
        self,
        *,
        command: Literal["new", "upload", "save"],
        list: str,
        data: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Import a list as a CSV file in steps: new (create), upload (data, repeated in chunks), save (save and apply).

        The shell-script example sends the arguments as a form body, with the list name as list and the CSV
        chunk as data.

        Access: admin.
        """
        self._run(OPS.upload_list, None, {"command": command, "list": list, "data": data}, request_options)

    @overload
    def search_events(
        self, request: SearchEventsRequest, /, *, request_options: RequestOptions | None = None
    ) -> EventSearchResult: ...
    @overload
    def search_events(
        self,
        /,
        *,
        timestampfrom: int | MISSING = MISSING,
        timestampto: int | MISSING = MISSING,
        text: str | MISSING = MISSING,
        place_desc: str | MISSING = MISSING,
        country: str | MISSING = MISSING,
        car_type: Literal[1, 2, 32] | MISSING = MISSING,
        car_color: Literal[65536, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10] | MISSING = MISSING,
        roi_id: int | MISSING = MISSING,
        car_direction: int | MISSING = MISSING,
        car_view: Literal[0, 1] | MISSING = MISSING,
        action: Literal[0, 1] | MISSING = MISSING,
        offset: int | MISSING = MISSING,
        limit: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> EventSearchResult: ...
    def search_events(
        self,
        request: SearchEventsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> EventSearchResult:
        """Search recognition events. Access: admin."""
        return self._run(OPS.search_events, request, kwargs, request_options)

    def get_statistics(
        self, *, limit: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> Statistics:
        """Statistics: counts by direction, list and area of interest.

        limit=0 returns the statistics only, without event records.

        Access: admin.
        """
        return self._run(OPS.get_statistics, None, {"limit": limit}, request_options)

    def set_2n_config(self, config: str, *, request_options: RequestOptions | None = None) -> None:
        """Configure the 2N integration.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        self._run(OPS.set_2n_config, None, {"config": config}, request_options)

    def set_genetec_config(self, config: str, *, request_options: RequestOptions | None = None) -> None:
        """Configure the Genetec integration.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        self._run(OPS.set_genetec_config, None, {"config": config}, request_options)

    def set_settings(self, configuration: str, *, request_options: RequestOptions | None = None) -> None:
        """Set the ALPV settings, for example the Area of Interest.

        Posts a <configuration> XML document. Whether elements left out keep their current values is not
        documented.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_settings, None, {"configuration": configuration}, request_options)

    def get_push_config(self, profile: PushProfile, *, request_options: RequestOptions | None = None) -> PushConfig:
        """Get the configuration of a push event profile. Access: admin."""
        return self._run(OPS.get_push_config, None, {"profile": profile}, request_options)

    def set_push_config(
        self, profile: PushProfile, config: str, *, request_options: RequestOptions | None = None
    ) -> None:
        """Update the configuration of a push event profile.

        The device answers with the stored <cloud_config> (shown for HTTP and FTP in the docs).

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        self._run(OPS.set_push_config, None, {"profile": profile, "config": config}, request_options)

    def set_heartbeat_config(self, config: str, *, request_options: RequestOptions | None = None) -> None:
        """Configure the heartbeat service.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        self._run(OPS.set_heartbeat_config, None, {"config": config}, request_options)

    @overload
    def set_heartbeat_data(
        self, request: SetHeartbeatDataRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_heartbeat_data(self, data: HeartbeatData, /, *, request_options: RequestOptions | None = None) -> None: ...
    def set_heartbeat_data(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Choose the fields of the heartbeat message.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetHeartbeatDataRequest):
            kwargs = bind_positional(OPS.set_heartbeat_data, ("data",), (request, *args), kwargs)
            request = None
        self._run(OPS.set_heartbeat_data, request, kwargs, request_options)

    @overload
    def set_direction(
        self, request: SetDirectionRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_direction(self, config: DirectionConfig, /, *, request_options: RequestOptions | None = None) -> None: ...
    def set_direction(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Change the car direction angle of the regions of interest.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetDirectionRequest):
            kwargs = bind_positional(OPS.set_direction, ("config",), (request, *args), kwargs)
            request = None
        self._run(OPS.set_direction, request, kwargs, request_options)

    @overload
    def set_list_settings(
        self, request: SetListSettingsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_list_settings(
        self, settings: ListSettings, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    def set_list_settings(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Change the list settings, including list names (rename lists).

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetListSettingsRequest):
            kwargs = bind_positional(OPS.set_list_settings, ("settings",), (request, *args), kwargs)
            request = None
        self._run(OPS.set_list_settings, request, kwargs, request_options)

    def get_list(self, list_file: ListFile, *, request_options: RequestOptions | None = None) -> PlateListContent:
        """Get the entries of the allow, block or custom list. Access: admin."""
        return self._run(OPS.get_list, None, {"list_file": list_file}, request_options)

    def add_plates(self, list_file: ListFile, plates: str, *, request_options: RequestOptions | None = None) -> None:
        """Add a batch of plates to the allow, block or custom list. Access: admin."""
        self._run(OPS.add_plates, None, {"list_file": list_file, "plates": plates}, request_options)


class AsyncLicensePlateVerifierApi(AsyncApi):
    """License plate verifier API (``license-plate-verifier``)."""

    INFO = INFO

    async def get_2n_config(self, *, request_options: RequestOptions | None = None) -> TwoNConfig:
        """Get 2N integration settings. Access: admin."""
        return await self._run(OPS.get_2n_config, None, {}, request_options)

    async def get_genetec_config(self, *, request_options: RequestOptions | None = None) -> GenetecConfig:
        """Get Genetec integration settings. Access: admin."""
        return await self._run(OPS.get_genetec_config, None, {}, request_options)

    async def get_settings(self, *, request_options: RequestOptions | None = None) -> ET.Element:
        """Get the ALPV settings as the complete <configuration> XML element.

        The docs give a sample reply but no field table, so the result is the parsed XML root element.

        Access: admin.
        """
        return await self._run(OPS.get_settings, None, {}, request_options)

    async def get_roi(self, *, request_options: RequestOptions | None = None) -> str:
        """Get the Area of Interest configuration as text.

        The reply is a <pre> block listing the active ROI and its corner points.

        Access: admin.
        """
        return await self._run(OPS.get_roi, None, {}, request_options)

    async def get_list_settings(self, *, request_options: RequestOptions | None = None) -> ListSettings:
        """Get the list settings (allow, block and custom lists with schedules and modes).

        Access: admin.
        """
        return await self._run(OPS.get_list_settings, None, {}, request_options)

    async def add_plate(self, plate: str, list: ListName, *, request_options: RequestOptions | None = None) -> None:
        """Add a single plate to the allow, block or custom list. Access: admin."""
        await self._run(OPS.add_plate, None, {"plate": plate, "list": list}, request_options)

    async def delete_plate(self, plate: str, list: ListName, *, request_options: RequestOptions | None = None) -> None:
        """Remove a single plate from the allow, block or custom list. Access: admin."""
        await self._run(OPS.delete_plate, None, {"plate": plate, "list": list}, request_options)

    async def export_allow_list(self, *, request_options: RequestOptions | None = None) -> str:
        """Export the allow list as text lines 'PLATE,MM-DD-YYYY,description'. Access: admin."""
        return await self._run(OPS.export_allow_list, None, {}, request_options)

    async def export_block_list(self, *, request_options: RequestOptions | None = None) -> str:
        """Export the block list as text lines 'PLATE,MM-DD-YYYY,description'. Access: admin."""
        return await self._run(OPS.export_block_list, None, {}, request_options)

    async def export_custom_list(self, *, request_options: RequestOptions | None = None) -> str:
        """Export the custom list as text lines 'PLATE,MM-DD-YYYY,description'. Access: admin."""
        return await self._run(OPS.export_custom_list, None, {}, request_options)

    async def upload_list(
        self,
        *,
        command: Literal["new", "upload", "save"],
        list: str,
        data: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Import a list as a CSV file in steps: new (create), upload (data, repeated in chunks), save (save and apply).

        The shell-script example sends the arguments as a form body, with the list name as list and the CSV
        chunk as data.

        Access: admin.
        """
        await self._run(OPS.upload_list, None, {"command": command, "list": list, "data": data}, request_options)

    @overload
    async def search_events(
        self, request: SearchEventsRequest, /, *, request_options: RequestOptions | None = None
    ) -> EventSearchResult: ...
    @overload
    async def search_events(
        self,
        /,
        *,
        timestampfrom: int | MISSING = MISSING,
        timestampto: int | MISSING = MISSING,
        text: str | MISSING = MISSING,
        place_desc: str | MISSING = MISSING,
        country: str | MISSING = MISSING,
        car_type: Literal[1, 2, 32] | MISSING = MISSING,
        car_color: Literal[65536, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10] | MISSING = MISSING,
        roi_id: int | MISSING = MISSING,
        car_direction: int | MISSING = MISSING,
        car_view: Literal[0, 1] | MISSING = MISSING,
        action: Literal[0, 1] | MISSING = MISSING,
        offset: int | MISSING = MISSING,
        limit: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> EventSearchResult: ...
    async def search_events(
        self,
        request: SearchEventsRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> EventSearchResult:
        """Search recognition events. Access: admin."""
        return await self._run(OPS.search_events, request, kwargs, request_options)

    async def get_statistics(
        self, *, limit: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> Statistics:
        """Statistics: counts by direction, list and area of interest.

        limit=0 returns the statistics only, without event records.

        Access: admin.
        """
        return await self._run(OPS.get_statistics, None, {"limit": limit}, request_options)

    async def set_2n_config(self, config: str, *, request_options: RequestOptions | None = None) -> None:
        """Configure the 2N integration.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        await self._run(OPS.set_2n_config, None, {"config": config}, request_options)

    async def set_genetec_config(self, config: str, *, request_options: RequestOptions | None = None) -> None:
        """Configure the Genetec integration.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        await self._run(OPS.set_genetec_config, None, {"config": config}, request_options)

    async def set_settings(self, configuration: str, *, request_options: RequestOptions | None = None) -> None:
        """Set the ALPV settings, for example the Area of Interest.

        Posts a <configuration> XML document. Whether elements left out keep their current values is not
        documented.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_settings, None, {"configuration": configuration}, request_options)

    async def get_push_config(
        self, profile: PushProfile, *, request_options: RequestOptions | None = None
    ) -> PushConfig:
        """Get the configuration of a push event profile. Access: admin."""
        return await self._run(OPS.get_push_config, None, {"profile": profile}, request_options)

    async def set_push_config(
        self, profile: PushProfile, config: str, *, request_options: RequestOptions | None = None
    ) -> None:
        """Update the configuration of a push event profile.

        The device answers with the stored <cloud_config> (shown for HTTP and FTP in the docs).

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        await self._run(OPS.set_push_config, None, {"profile": profile, "config": config}, request_options)

    async def set_heartbeat_config(self, config: str, *, request_options: RequestOptions | None = None) -> None:
        """Configure the heartbeat service.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        await self._run(OPS.set_heartbeat_config, None, {"config": config}, request_options)

    @overload
    async def set_heartbeat_data(
        self, request: SetHeartbeatDataRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_heartbeat_data(
        self, data: HeartbeatData, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_heartbeat_data(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Choose the fields of the heartbeat message.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetHeartbeatDataRequest):
            kwargs = bind_positional(OPS.set_heartbeat_data, ("data",), (request, *args), kwargs)
            request = None
        await self._run(OPS.set_heartbeat_data, request, kwargs, request_options)

    @overload
    async def set_direction(
        self, request: SetDirectionRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_direction(
        self, config: DirectionConfig, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_direction(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Change the car direction angle of the regions of interest.

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetDirectionRequest):
            kwargs = bind_positional(OPS.set_direction, ("config",), (request, *args), kwargs)
            request = None
        await self._run(OPS.set_direction, request, kwargs, request_options)

    @overload
    async def set_list_settings(
        self, request: SetListSettingsRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_list_settings(
        self, settings: ListSettings, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_list_settings(
        self, request: Any = MISSING, /, *args: Any, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Change the list settings, including list names (rename lists).

        Replaces the whole configuration; fields left out return to their defaults. Access: admin.
        """
        if request is MISSING:
            request = None
        elif args or not isinstance(request, SetListSettingsRequest):
            kwargs = bind_positional(OPS.set_list_settings, ("settings",), (request, *args), kwargs)
            request = None
        await self._run(OPS.set_list_settings, request, kwargs, request_options)

    async def get_list(self, list_file: ListFile, *, request_options: RequestOptions | None = None) -> PlateListContent:
        """Get the entries of the allow, block or custom list. Access: admin."""
        return await self._run(OPS.get_list, None, {"list_file": list_file}, request_options)

    async def add_plates(
        self, list_file: ListFile, plates: str, *, request_options: RequestOptions | None = None
    ) -> None:
        """Add a batch of plates to the allow, block or custom list. Access: admin."""
        await self._run(OPS.add_plates, None, {"list_file": list_file, "plates": plates}, request_options)
