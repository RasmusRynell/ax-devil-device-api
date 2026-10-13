# GENERATED from specs/apis/network-video/m12-lens-selection.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Select M12 lenses (field of view / distortion) for individual camera sensors in products controlling a remote PTZ camera with exchangeable lenses.

Docs: https://developer.axis.com/vapix/network-video/m12-lens-selection/
"""

from __future__ import annotations

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class Lens(Model):
    lens_id: int = Field(validation_alias="lensId", serialization_alias="lensId")
    """The lens ID."""
    lens_name: str = Field(validation_alias="lensName", serialization_alias="lensName")
    """The lens name."""
    sensor_ids: list[int] | None = Field(default=None, validation_alias="sensorIds", serialization_alias="sensorIds")
    """Sensor IDs where the lens is used; only returned when ``listSensorIds`` was set."""


class CurrentLens(Model):
    sensor_id: int = Field(validation_alias="sensorId", serialization_alias="sensorId")
    """The sensor ID."""
    lens_id: int = Field(validation_alias="lensId", serialization_alias="lensId")
    """The lens ID."""
    lens_name: str = Field(validation_alias="lensName", serialization_alias="lensName")
    """The lens name."""


class GetSupportedLensesRequest(Model):
    list_sensor_ids: bool | None = Field(
        default=None, validation_alias="listSensorIds", serialization_alias="listSensorIds"
    )
    """Optional. The user sets this value and the server will add an array of sensor IDs for the currently used lens."""


class GetCurrentLensesRequest(Model):
    sensor_id: int | None = Field(default=None, validation_alias="sensorId", serialization_alias="sensorId")
    """Optional. The server will get the current lens for the specified sensor ID; omitted = all sensors."""


class SetCurrentLensRequest(Model):
    sensor_id: int = Field(validation_alias="sensorId", serialization_alias="sensorId")
    """The sensor ID that should be set."""
    lens_id: int = Field(validation_alias="lensId", serialization_alias="lensId")
    """The lens ID that should be set."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/m12-lensselection.cgi"

INFO = ApiInfo(
    id="m12-lens-selection",
    name="M12 Lens Selection API",
    family=Family.JSONRPC,
    major=2,
    known_versions=(ApiVersion(2, 1),),
    discovery=(
        ParamDiscovery("Properties.M12LensSelection.M12LensSelection", "yes"),
        ParamDiscovery("Properties.M12LensSelection.Version", "1.00"),
    ),
    docs=("https://developer.axis.com/vapix/network-video/m12-lens-selection/",),
    errors={
        1000: ErrorCode("Invalid parameter value.", "invalid_argument"),
        1001: ErrorCode("Invalid sensor.", "invalid_argument"),
        1002: ErrorCode("Unsupported lens.", "unsupported"),
        2000: ErrorCode("Out of memory.", "internal"),
        2001: ErrorCode("Access forbidden (similar to HTTP 403).", "access_denied"),
        2002: ErrorCode("HTTP request type not supported. Only POST supported.", "unsupported"),
        2003: ErrorCode("The requested API version is not supported.", "unsupported"),
        2004: ErrorCode("Method not supported.", "unsupported"),
        4000: ErrorCode("The provided JSON input was invalid.", "invalid_argument"),
        4001: ErrorCode("A mandatory input parameter was not found in the input.", "invalid_argument"),
        4002: ErrorCode("The type of a provided JSON parameter was incorrect.", "invalid_argument"),
        8000: ErrorCode("Internal error, could not complete request.", "internal"),
    },
)


class OPS:
    get_supported_lenses = Operation(
        INFO,
        "get_supported_lenses",
        JsonRpcBinding("getSupportedLenses", PATH),
        params=GetSupportedLensesRequest,
        result=list[Lens],
        access="operator",
        effect="read",
    )
    get_current_lenses = Operation(
        INFO,
        "get_current_lenses",
        JsonRpcBinding("getCurrentLenses", PATH),
        params=GetCurrentLensesRequest,
        result=list[CurrentLens],
        access="operator",
        effect="read",
    )
    set_current_lens = Operation(
        INFO,
        "set_current_lens",
        JsonRpcBinding("setCurrentLens", PATH),
        params=SetCurrentLensRequest,
        access="operator",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class M12LensSelectionApi(SyncApi):
    """M12 Lens Selection API (``m12-lens-selection``, version 2)."""

    INFO = INFO

    def get_supported_lenses(
        self, *, list_sensor_ids: bool | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> list[Lens]:
        """Return a list of supported lenses. Access: operator."""
        return self._run(OPS.get_supported_lenses, None, {"list_sensor_ids": list_sensor_ids}, request_options)

    def get_current_lenses(
        self, *, sensor_id: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> list[CurrentLens]:
        """Return the current lenses used by the camera sensors. Access: operator."""
        return self._run(OPS.get_current_lenses, None, {"sensor_id": sensor_id}, request_options)

    def set_current_lens(self, *, sensor_id: int, lens_id: int, request_options: RequestOptions | None = None) -> None:
        """Set the current lens for one of the sensors.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_current_lens, None, {"sensor_id": sensor_id, "lens_id": lens_id}, request_options)


class AsyncM12LensSelectionApi(AsyncApi):
    """M12 Lens Selection API (``m12-lens-selection``, version 2)."""

    INFO = INFO

    async def get_supported_lenses(
        self, *, list_sensor_ids: bool | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> list[Lens]:
        """Return a list of supported lenses. Access: operator."""
        return await self._run(OPS.get_supported_lenses, None, {"list_sensor_ids": list_sensor_ids}, request_options)

    async def get_current_lenses(
        self, *, sensor_id: int | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> list[CurrentLens]:
        """Return the current lenses used by the camera sensors. Access: operator."""
        return await self._run(OPS.get_current_lenses, None, {"sensor_id": sensor_id}, request_options)

    async def set_current_lens(
        self, *, sensor_id: int, lens_id: int, request_options: RequestOptions | None = None
    ) -> None:
        """Set the current lens for one of the sensors.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_current_lens, None, {"sensor_id": sensor_id, "lens_id": lens_id}, request_options)
