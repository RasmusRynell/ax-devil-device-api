# GENERATED from specs/apis/network-video/pt-remote-calibration.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Calibrate pan/tilt coordinates of a remote PTZ camera against a local camera (AXIS Q6000-E): start/abort, select target, on target, save, status.

Docs: https://developer.axis.com/vapix/network-video/integrating-axis-q6000-e/
"""

from __future__ import annotations

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
    """The version number of the XML schema, major.minor."""
    deprecated: bool | None = Field(default=None, validation_alias="Deprecated", serialization_alias="Deprecated")
    """If true, this version of the XML schema is deprecated and should not be used. Defaults to false."""


class SchemaVersions(Model):
    schema_version: list[SchemaVersion] = Field(validation_alias="SchemaVersion", serialization_alias="SchemaVersion")


class SelectTargetResult(Model):
    """Empty for the first target of a calibration; later targets return the approximate remote pan/tilt."""

    pan: float | None = Field(default=None, validation_alias="Pan", serialization_alias="Pan")
    """Approximate value for the remote PTZ camera pan coordinate, in degrees."""
    tilt: float | None = Field(default=None, validation_alias="Tilt", serialization_alias="Tilt")
    """Approximate value for the remote PTZ camera tilt coordinate, in degrees."""


class CurrentTarget(Model):
    x: float = Field(validation_alias="X", serialization_alias="X")
    """Normalized x pixel coordinate of the current calibration target (-1.0 is the left edge, 1.0 the right edge)."""
    y: float = Field(validation_alias="Y", serialization_alias="Y")
    """Normalized y pixel coordinate of the current calibration target (-1.0 is the bottom edge, 1.0 the top edge)."""


class CalibrationInformation(Model):
    camera: int = Field(validation_alias="Camera", serialization_alias="Camera")
    """The local camera (camera head) used in the calibration process."""
    current_target: CurrentTarget = Field(validation_alias="CurrentTarget", serialization_alias="CurrentTarget")


class CameraCalibration(Model):
    id: int = Field(validation_alias="Id", serialization_alias="Id")
    """The camera number."""
    calibrated: int = Field(validation_alias="Calibrated", serialization_alias="Calibrated", ge=0)
    """0 = the camera is not calibrated, 1 and above = calibrated."""


class CalibrationStatus(Model):
    camera: list[CameraCalibration] = Field(validation_alias="Camera", serialization_alias="Camera")


class StartRequest(Model):
    schemaversion: str = Field(pattern=r"^[0-9]+(\.[0-9]+)?$")
    """The version of the XML schema to use for the response, in the form major[.minor]. The major version is required; if the minor version is omitted the latest minor version is used."""
    camera: int | None = Field(default=None, ge=1)
    """The camera (camera head) to use for calibration; the number of cameras is given by ImageSource.NbrOfSources. Defaults to 1. Default: 1."""


class AbortRequest(Model):
    schemaversion: str = Field(pattern=r"^[0-9]+(\.[0-9]+)?$")
    """The version of the XML schema to use for the response, in the form major[.minor]. The major version is required; if the minor version is omitted the latest minor version is used."""


class SelectTargetRequest(Model):
    schemaversion: str = Field(pattern=r"^[0-9]+(\.[0-9]+)?$")
    """The version of the XML schema to use for the response, in the form major[.minor]. The major version is required; if the minor version is omitted the latest minor version is used."""
    x: float = Field(ge=-1.0, le=1.0)
    """Normalized x coordinate in the local product coordinate system; (-1,-1) is the bottom left, (0,0) the center and (1,1) the upper right corner."""
    y: float = Field(ge=-1.0, le=1.0)
    """Normalized y coordinate in the local product coordinate system."""


class OnTargetRequest(Model):
    schemaversion: str = Field(pattern=r"^[0-9]+(\.[0-9]+)?$")
    """The version of the XML schema to use for the response, in the form major[.minor]. The major version is required; if the minor version is omitted the latest minor version is used."""
    pan: float | None = None
    """Pan coordinate (degrees) of the remote PTZ camera; product dependent (see PTZ.Limit.MinPan and PTZ.Limit.MaxPan). If omitted, read from local status."""
    tilt: float | None = None
    """Tilt coordinate (degrees) of the remote PTZ camera; product dependent (see PTZ.Limit.MinTilt and PTZ.Limit.MaxTilt). If omitted, read from local status."""


class SaveRequest(Model):
    schemaversion: str = Field(pattern=r"^[0-9]+(\.[0-9]+)?$")
    """The version of the XML schema to use for the response, in the form major[.minor]. The major version is required; if the minor version is omitted the latest minor version is used."""


class GetInformationRequest(Model):
    schemaversion: str = Field(pattern=r"^[0-9]+(\.[0-9]+)?$")
    """The version of the XML schema to use for the response, in the form major[.minor]. The major version is required; if the minor version is omitted the latest minor version is used."""


class IsCalibratedRequest(Model):
    schemaversion: str = Field(pattern=r"^[0-9]+(\.[0-9]+)?$")
    """The version of the XML schema to use for the response, in the form major[.minor]. The major version is required; if the minor version is omitted the latest minor version is used."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/ptremotecalibration/start.cgi"

INFO = ApiInfo(
    id="pt-remote-calibration",
    name="Remote PT Coordinate Calibration API",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.PTRemoteCalibration.PTRemoteCalibration", "yes"),),
    docs=("https://developer.axis.com/vapix/network-video/integrating-axis-q6000-e/",),
    errors={
        10: ErrorCode("Error while processing the request."),
        20: ErrorCode("Invalid request.", "invalid_argument"),
        40: ErrorCode("Specified version is not supported.", "unsupported"),
    },
)


class OPS:
    start = Operation(
        INFO,
        "start",
        CgiBinding(PATH, args=(CgiArg("schemaversion"), CgiArg("camera")), reply=Xml()),
        params=StartRequest,
        access="admin",
        effect="action",
        errors={
            50: ErrorCode(
                "Calibration is already ongoing. It is not possible to start a new calibration.", "unavailable"
            )
        },
    )
    abort = Operation(
        INFO,
        "abort",
        CgiBinding("/axis-cgi/ptremotecalibration/abort.cgi", args=(CgiArg("schemaversion"),), reply=Xml()),
        params=AbortRequest,
        access="admin",
        effect="action",
        errors={54: ErrorCode("No calibration is ongoing.", "unavailable")},
    )
    select_target = Operation(
        INFO,
        "select_target",
        CgiBinding(
            "/axis-cgi/ptremotecalibration/selecttarget.cgi",
            args=(CgiArg("schemaversion"), CgiArg("x"), CgiArg("y")),
            reply=Xml(
                map=XmlMap(
                    fields=(XmlField("Pan", source="child"), XmlField("Tilt", source="child")),
                    root="SelectTargetSuccess",
                )
            ),
        ),
        params=SelectTargetRequest,
        result=SelectTargetResult,
        access="admin",
        effect="action",
        errors={54: ErrorCode("No calibration is ongoing.", "unavailable")},
    )
    on_target = Operation(
        INFO,
        "on_target",
        CgiBinding(
            "/axis-cgi/ptremotecalibration/ontarget.cgi",
            args=(CgiArg("schemaversion"), CgiArg("pan"), CgiArg("tilt")),
            reply=Xml(),
        ),
        params=OnTargetRequest,
        access="admin",
        effect="action",
        errors={
            52: ErrorCode(
                "The pan/tilt coordinates and the selected pixel coordinates (x and y) could not be matched.",
                "invalid_argument",
            ),
            53: ErrorCode("No pixel coordinates are selected.", "unavailable"),
            54: ErrorCode("No calibration is ongoing.", "unavailable"),
        },
    )
    save = Operation(
        INFO,
        "save",
        CgiBinding("/axis-cgi/ptremotecalibration/save.cgi", args=(CgiArg("schemaversion"),), reply=Xml()),
        params=SaveRequest,
        access="admin",
        effect="action",
        errors={
            51: ErrorCode("A satisfying coordinate matching could not be found.", "unavailable"),
            54: ErrorCode("No calibration is ongoing.", "unavailable"),
        },
    )
    get_information = Operation(
        INFO,
        "get_information",
        CgiBinding(
            "/axis-cgi/ptremotecalibration/getinformation.cgi",
            args=(CgiArg("schemaversion"),),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField("Camera", source="child"),
                        XmlField(
                            "CurrentTarget",
                            source="path",
                            nested=XmlMap(fields=(XmlField("X", source="child"), XmlField("Y", source="child"))),
                        ),
                    ),
                    root="GetInformationSuccess",
                )
            ),
        ),
        params=GetInformationRequest,
        result=CalibrationInformation,
        access="admin",
        effect="read",
        errors={54: ErrorCode("No calibration is ongoing.", "unavailable")},
    )
    is_calibrated = Operation(
        INFO,
        "is_calibrated",
        CgiBinding(
            "/axis-cgi/ptremotecalibration/iscalibrated.cgi",
            args=(CgiArg("schemaversion"),),
            reply=Xml(
                map=XmlMap(
                    fields=(
                        XmlField(
                            "Camera",
                            source="path",
                            many=True,
                            nested=XmlMap(
                                fields=(XmlField("Id", source="child"), XmlField("Calibrated", source="child"))
                            ),
                        ),
                    ),
                    root="IsCalibratedSuccess",
                )
            ),
        ),
        params=IsCalibratedRequest,
        result=CalibrationStatus,
        access="admin",
        effect="read",
        errors={54: ErrorCode("No calibration is ongoing.", "unavailable")},
    )
    get_schema_versions = Operation(
        INFO,
        "get_schema_versions",
        CgiBinding(
            "/axis-cgi/ptremotecalibration/schemaversions.cgi",
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
                    root="SchemaVersionsSuccess",
                )
            ),
        ),
        result=SchemaVersions,
        access="admin",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class PtRemoteCalibrationApi(SyncApi):
    """Remote PT Coordinate Calibration API (``pt-remote-calibration``)."""

    INFO = INFO

    def start(
        self, *, schemaversion: str, camera: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Start calibration. Access: admin."""
        self._run(OPS.start, None, {"schemaversion": schemaversion, "camera": camera}, request_options)

    def abort(self, *, schemaversion: str, request_options: RequestOptions | None = None) -> None:
        """Abort an ongoing calibration; all unsaved data will be lost. Access: admin."""
        self._run(OPS.abort, None, {"schemaversion": schemaversion}, request_options)

    def select_target(
        self, x: float, y: float, *, schemaversion: str, request_options: RequestOptions | None = None
    ) -> SelectTargetResult:
        """Select a calibration target (normalized x,y) in the image from the local product.

        Position the remote PTZ camera on the same point, then call on_target. Later calls before on_target
        replace the target. The first call of a calibration returns an empty result; later calls return an
        approximate pan/tilt for the remote camera.

        Access: admin.
        """
        return self._run(OPS.select_target, None, {"schemaversion": schemaversion, "x": x, "y": y}, request_options)

    def on_target(
        self,
        *,
        schemaversion: str,
        pan: float | MISSING = MISSING,
        tilt: float | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Inform the local product that the remote PTZ camera is positioned at the selected calibration target.

        Access: admin.
        """
        self._run(OPS.on_target, None, {"schemaversion": schemaversion, "pan": pan, "tilt": tilt}, request_options)

    def save(self, *, schemaversion: str, request_options: RequestOptions | None = None) -> None:
        """Save calibration data: creates the coordinate transformation and stops the calibration process.

        Access: admin.
        """
        self._run(OPS.save, None, {"schemaversion": schemaversion}, request_options)

    def get_information(
        self, *, schemaversion: str, request_options: RequestOptions | None = None
    ) -> CalibrationInformation:
        """Retrieve information about an ongoing calibration. Access: admin."""
        return self._run(OPS.get_information, None, {"schemaversion": schemaversion}, request_options)

    def is_calibrated(self, *, schemaversion: str, request_options: RequestOptions | None = None) -> CalibrationStatus:
        """List all cameras and whether they are calibrated. Access: admin."""
        return self._run(OPS.is_calibrated, None, {"schemaversion": schemaversion}, request_options)

    def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """List supported XML schema versions. Access: admin."""
        return self._run(OPS.get_schema_versions, None, {}, request_options)


class AsyncPtRemoteCalibrationApi(AsyncApi):
    """Remote PT Coordinate Calibration API (``pt-remote-calibration``)."""

    INFO = INFO

    async def start(
        self, *, schemaversion: str, camera: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Start calibration. Access: admin."""
        await self._run(OPS.start, None, {"schemaversion": schemaversion, "camera": camera}, request_options)

    async def abort(self, *, schemaversion: str, request_options: RequestOptions | None = None) -> None:
        """Abort an ongoing calibration; all unsaved data will be lost. Access: admin."""
        await self._run(OPS.abort, None, {"schemaversion": schemaversion}, request_options)

    async def select_target(
        self, x: float, y: float, *, schemaversion: str, request_options: RequestOptions | None = None
    ) -> SelectTargetResult:
        """Select a calibration target (normalized x,y) in the image from the local product.

        Position the remote PTZ camera on the same point, then call on_target. Later calls before on_target
        replace the target. The first call of a calibration returns an empty result; later calls return an
        approximate pan/tilt for the remote camera.

        Access: admin.
        """
        return await self._run(
            OPS.select_target, None, {"schemaversion": schemaversion, "x": x, "y": y}, request_options
        )

    async def on_target(
        self,
        *,
        schemaversion: str,
        pan: float | MISSING = MISSING,
        tilt: float | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Inform the local product that the remote PTZ camera is positioned at the selected calibration target.

        Access: admin.
        """
        await self._run(
            OPS.on_target, None, {"schemaversion": schemaversion, "pan": pan, "tilt": tilt}, request_options
        )

    async def save(self, *, schemaversion: str, request_options: RequestOptions | None = None) -> None:
        """Save calibration data: creates the coordinate transformation and stops the calibration process.

        Access: admin.
        """
        await self._run(OPS.save, None, {"schemaversion": schemaversion}, request_options)

    async def get_information(
        self, *, schemaversion: str, request_options: RequestOptions | None = None
    ) -> CalibrationInformation:
        """Retrieve information about an ongoing calibration. Access: admin."""
        return await self._run(OPS.get_information, None, {"schemaversion": schemaversion}, request_options)

    async def is_calibrated(
        self, *, schemaversion: str, request_options: RequestOptions | None = None
    ) -> CalibrationStatus:
        """List all cameras and whether they are calibrated. Access: admin."""
        return await self._run(OPS.is_calibrated, None, {"schemaversion": schemaversion}, request_options)

    async def get_schema_versions(self, *, request_options: RequestOptions | None = None) -> SchemaVersions:
        """List supported XML schema versions. Access: admin."""
        return await self._run(OPS.get_schema_versions, None, {}, request_options)
