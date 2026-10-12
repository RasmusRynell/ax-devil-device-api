# GENERATED from specs/apis/device-configuration/thermal-visual-fusion-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Control the thermal visual fusion view - base source, overlay transparency and alignment.

Docs: https://developer.axis.com/vapix/device-configuration/thermal-visual-fusion-configuration-api/
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

AbsCoordinate = Annotated[float, Field(ge=-1, le=1)]


class Alignment(Model):
    """Distance between the center of the thermal stream and the center of visual stream. Any part of the overlaid stream that is outside the base stream will be cropped out. Use the `[-1..1]` coordinate system."""

    x: AbsCoordinate | None = None
    """x-axis part of the alignment."""
    y: AbsCoordinate | None = None
    """y-axis part of the alignment."""


FusionModeEnum = Literal["VISUAL", "THERMAL"]
FusionMoveEnum = Literal["MOVE_LEFT", "MOVE_RIGHT", "MOVE_UP", "MOVE_DOWN"]
Transparency = Annotated[float, Field(ge=0, le=1)]


class ThermalVisualFusion(Model):
    """The whole API tree."""

    alignment: Alignment | None = None
    """Alignment of the overlaid stream."""
    fusion_mode: FusionModeEnum | None = Field(
        default=None, validation_alias="fusionMode", serialization_alias="fusionMode"
    )
    """The mode of the thermal visual fusion."""
    transparency: Transparency | None = None
    """Transparency of the overlaid stream."""


class SetAlignmentRequest(Model):
    alignment: Alignment
    """Alignment of the overlaid stream."""


class SetFusionModeRequest(Model):
    fusion_mode: FusionModeEnum = Field(validation_alias="fusionMode", serialization_alias="fusionMode")
    """The mode of the thermal visual fusion."""


class SetTransparencyRequest(Model):
    transparency: Transparency
    """Transparency of the overlaid stream."""


class UpdateAlignmentRequest(Model):
    fusion_move_alignment: FusionMoveEnum | None = Field(
        default=None, validation_alias="fusionMoveAlignment", serialization_alias="fusionMoveAlignment"
    )
    """What movement to apply to alignment in fusion."""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/thermal-visual-fusion/v1beta"

INFO = ApiInfo(
    id="thermal-visual-fusion-config",
    name="Thermal visual fusion configuration",
    family=Family.DCA,
    discovery=(DcaDiscovery("thermal-visual-fusion", "v1"),),
    docs=("https://developer.axis.com/vapix/device-configuration/thermal-visual-fusion-configuration-api/",),
)


class OPS:
    get_all = Operation(
        INFO, "get_all", DcaBinding("GET", ROOT), result=ThermalVisualFusion, access="viewer", effect="read"
    )
    get_alignment = Operation(
        INFO, "get_alignment", DcaBinding("GET", f"{ROOT}/alignment"), result=Alignment, access="viewer", effect="read"
    )
    set_alignment = Operation(
        INFO,
        "set_alignment",
        DcaBinding("PATCH", f"{ROOT}/alignment", body="value", body_field="alignment"),
        params=SetAlignmentRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_fusion_mode = Operation(
        INFO,
        "get_fusion_mode",
        DcaBinding("GET", f"{ROOT}/fusionMode"),
        result=FusionModeEnum,
        access="viewer",
        effect="read",
    )
    set_fusion_mode = Operation(
        INFO,
        "set_fusion_mode",
        DcaBinding("PATCH", f"{ROOT}/fusionMode", body="value", body_field="fusionMode"),
        params=SetFusionModeRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_transparency = Operation(
        INFO,
        "get_transparency",
        DcaBinding("GET", f"{ROOT}/transparency"),
        result=Transparency,
        access="viewer",
        effect="read",
    )
    set_transparency = Operation(
        INFO,
        "set_transparency",
        DcaBinding("PATCH", f"{ROOT}/transparency", body="value", body_field="transparency"),
        params=SetTransparencyRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    reset_alignment = Operation(
        INFO, "reset_alignment", DcaBinding("POST", f"{ROOT}/resetAlignment"), access="admin", effect="action"
    )
    update_alignment = Operation(
        INFO,
        "update_alignment",
        DcaBinding("POST", f"{ROOT}/updateAlignment", body="object"),
        params=UpdateAlignmentRequest,
        access="admin",
        effect="action",
    )


# ---------------------------------------------------------------------------
# API classes


class ThermalVisualFusionApi(SyncApi):
    """Thermal visual fusion configuration (``thermal-visual-fusion-config``, v1)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> ThermalVisualFusion:
        """All data of the Thermal visual fusion configuration API. Access: viewer."""
        return self._run(OPS.get_all, None, {}, request_options)

    def get_alignment(self, *, request_options: RequestOptions | None = None) -> Alignment:
        """Read the alignment of the overlaid stream. Access: viewer."""
        return self._run(OPS.get_alignment, None, {}, request_options)

    @overload
    def set_alignment(
        self, request: SetAlignmentRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_alignment(self, /, *, alignment: Alignment, request_options: RequestOptions | None = None) -> None: ...
    def set_alignment(
        self,
        request: SetAlignmentRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the alignment of the device. Changes only the fields given. Access: admin."""
        self._run(OPS.set_alignment, request, kwargs, request_options)

    def get_fusion_mode(self, *, request_options: RequestOptions | None = None) -> FusionModeEnum:
        """Read the fusion mode. Access: viewer."""
        return self._run(OPS.get_fusion_mode, None, {}, request_options)

    def set_fusion_mode(self, *, fusion_mode: FusionModeEnum, request_options: RequestOptions | None = None) -> None:
        """Set the fusion mode of the device. Changes only the fields given. Access: admin."""
        self._run(OPS.set_fusion_mode, None, {"fusion_mode": fusion_mode}, request_options)

    def get_transparency(self, *, request_options: RequestOptions | None = None) -> Transparency:
        """Read the transparency of the overlaid stream. Access: viewer."""
        return self._run(OPS.get_transparency, None, {}, request_options)

    def set_transparency(self, *, transparency: Transparency, request_options: RequestOptions | None = None) -> None:
        """Set the transparency of the device. Changes only the fields given. Access: admin."""
        self._run(OPS.set_transparency, None, {"transparency": transparency}, request_options)

    def reset_alignment(self, *, request_options: RequestOptions | None = None) -> None:
        """Reset the alignment to factory settings. Access: admin."""
        self._run(OPS.reset_alignment, None, {}, request_options)

    def update_alignment(
        self,
        *,
        fusion_move_alignment: FusionMoveEnum | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update alignment of the fusion stream. Access: admin."""
        self._run(OPS.update_alignment, None, {"fusion_move_alignment": fusion_move_alignment}, request_options)


class AsyncThermalVisualFusionApi(AsyncApi):
    """Thermal visual fusion configuration (``thermal-visual-fusion-config``, v1)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> ThermalVisualFusion:
        """All data of the Thermal visual fusion configuration API. Access: viewer."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def get_alignment(self, *, request_options: RequestOptions | None = None) -> Alignment:
        """Read the alignment of the overlaid stream. Access: viewer."""
        return await self._run(OPS.get_alignment, None, {}, request_options)

    @overload
    async def set_alignment(
        self, request: SetAlignmentRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_alignment(
        self, /, *, alignment: Alignment, request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_alignment(
        self,
        request: SetAlignmentRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the alignment of the device. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_alignment, request, kwargs, request_options)

    async def get_fusion_mode(self, *, request_options: RequestOptions | None = None) -> FusionModeEnum:
        """Read the fusion mode. Access: viewer."""
        return await self._run(OPS.get_fusion_mode, None, {}, request_options)

    async def set_fusion_mode(
        self, *, fusion_mode: FusionModeEnum, request_options: RequestOptions | None = None
    ) -> None:
        """Set the fusion mode of the device. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_fusion_mode, None, {"fusion_mode": fusion_mode}, request_options)

    async def get_transparency(self, *, request_options: RequestOptions | None = None) -> Transparency:
        """Read the transparency of the overlaid stream. Access: viewer."""
        return await self._run(OPS.get_transparency, None, {}, request_options)

    async def set_transparency(
        self, *, transparency: Transparency, request_options: RequestOptions | None = None
    ) -> None:
        """Set the transparency of the device. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_transparency, None, {"transparency": transparency}, request_options)

    async def reset_alignment(self, *, request_options: RequestOptions | None = None) -> None:
        """Reset the alignment to factory settings. Access: admin."""
        await self._run(OPS.reset_alignment, None, {}, request_options)

    async def update_alignment(
        self,
        *,
        fusion_move_alignment: FusionMoveEnum | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update alignment of the fusion stream. Access: admin."""
        await self._run(OPS.update_alignment, None, {"fusion_move_alignment": fusion_move_alignment}, request_options)
