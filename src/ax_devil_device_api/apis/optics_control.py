# GENERATED from specs/apis/network-video/optics-control.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Control zoom and focus optics: absolute and relative focus, magnification, autofocus and focus window, calibration, reset, temperature and IR compensation and the IR cut filter.

Docs: https://developer.axis.com/vapix/network-video/optics-control/
"""

from __future__ import annotations

from typing import Any, Literal, overload

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

IrCutFilterState = Literal["on", "off", "auto"]
RelativeStepType = Literal["+bigStep", "-bigStep", "+smallStep", "-smallStep", "numerical"]
Capability = Literal[
    "focus", "zoom", "irCutFilter", "calibrateFocus", "calibrateZoom", "compensateTemperature", "compensateIr"
]


class Optics(Model):
    """Status of one optics unit."""

    optics_id: str = Field(validation_alias="opticsId", serialization_alias="opticsId")
    """The optics ID."""
    focus_position: float | None = Field(
        default=None, validation_alias="focusPosition", serialization_alias="focusPosition"
    )
    """The current position of the focus shown as a value between 0 and 1."""
    focus_moving: bool | None = Field(default=None, validation_alias="focusMoving", serialization_alias="focusMoving")
    """Shows if the focus is moving."""
    focus_window_upper_left_x: float | None = Field(
        default=None, validation_alias="focusWindowUpperLeftX", serialization_alias="focusWindowUpperLeftX"
    )
    """The distance from the upper left corner of the image to the upper left corner of the focus window on the X-plane. Has a value between 0 and 1, with 0 being the top edge of the image and 1 being the bottom."""
    focus_window_upper_left_y: float | None = Field(
        default=None, validation_alias="focusWindowUpperLeftY", serialization_alias="focusWindowUpperLeftY"
    )
    """The distance from the upper left corner of the image to the upper left corner of the focus window on the Y-plane. Has a value between 0 and 1, with 0 being the top edge of the image and 1 being the bottom."""
    focus_window_width: float | None = Field(
        default=None, validation_alias="focusWindowWidth", serialization_alias="focusWindowWidth"
    )
    """The width of the focus window in a value between 0 and 1. represents the window having 100% width of the image. Please note that `focusWindowUpperLeftX+focusWindowWidth` can not exceed 1."""
    focus_window_height: float | None = Field(
        default=None, validation_alias="focusWindowHeight", serialization_alias="focusWindowHeight"
    )
    """The height of the focus window in a value between 0 and 1. 1 represents the window having 100% height of the image. Please not that `focusWindowUpperLeftY+focusWindowHeight` can not exceed 1."""
    magnification: float | None = None
    """The current magnification of the zoom lens. This is omitted if the optics doesn’t support zoom."""
    zoom_moving: bool | None = Field(default=None, validation_alias="zoomMoving", serialization_alias="zoomMoving")
    """Shows if the zoom lens is moving. This is omitted if the optics doesn’t support zoom."""
    temperature_compensation: bool | None = Field(
        default=None, validation_alias="temperatureCompensation", serialization_alias="temperatureCompensation"
    )
    """Shows if the temperature compensation is enabled."""
    ir_cut_filter_state: IrCutFilterState | None = Field(
        default=None, validation_alias="irCutFilterState", serialization_alias="irCutFilterState"
    )
    """Shows the current IRCut Filter setting. Possible vaues are: `on`: Filter is forced on. `off`: Filter is forced off. `auto`: Filter state is set by software algorithms."""
    ir_compensation: bool | None = Field(
        default=None, validation_alias="irCompensation", serialization_alias="irCompensation"
    )
    """Shows if the IR compensation is enabled."""


class OpticsList(Model):
    number_of_optics: int = Field(validation_alias="numberOfOptics", serialization_alias="numberOfOptics", ge=0, le=255)
    """The number of optics available on the device."""
    optics: list[Optics] | None = None
    """Omitted if `numberOfOptics` is zero."""


class OpticsCapabilities(Model):
    """Capabilities of one optics unit."""

    optics_id: str = Field(validation_alias="opticsId", serialization_alias="opticsId")
    """The optics ID."""
    capabilities: list[Capability] | None = None
    """The supported capabilities."""
    max_magnification: float | None = Field(
        default=None, validation_alias="maxMagnification", serialization_alias="maxMagnification"
    )
    """The maximum possible magnification that can be set. Only available for devices where zoom is available."""


class CapabilitiesList(Model):
    number_of_optics: int = Field(validation_alias="numberOfOptics", serialization_alias="numberOfOptics", ge=0, le=255)
    """The number of optics available on the device."""
    optics: list[OpticsCapabilities] | None = None
    """Omitted if `numberOfOptics` is zero."""


class SetFocusRequestOpticsItem(Model):
    optics_id: str = Field(validation_alias="opticsId", serialization_alias="opticsId")
    """The optics ID to set the focus on."""
    position: float = Field(ge=0, le=1)
    """The new focus position, a value between 0 and 1."""


class SetFocusRequest(Model):
    optics: list[SetFocusRequestOpticsItem]
    """The optics units to apply the change to."""


class SetRelativeFocusRequestOpticsItem(Model):
    optics_id: str = Field(validation_alias="opticsId", serialization_alias="opticsId")
    """The optics ID to change the relative focus on."""
    type: RelativeStepType
    """The step size: +bigStep, -bigStep, +smallStep, -smallStep, or numerical to use value."""
    value: float | None = None
    """The desired offset. Used when type is numerical."""


class SetRelativeFocusRequest(Model):
    optics: list[SetRelativeFocusRequestOpticsItem]
    """The optics units to apply the change to."""


class SetMagnificationRequestOpticsItem(Model):
    optics_id: str = Field(validation_alias="opticsId", serialization_alias="opticsId")
    """The optics ID to set magnification on."""
    magnification: float = Field(ge=1)
    """The new magnification, between 1 and maxMagnification from get_capabilities."""


class SetMagnificationRequest(Model):
    optics: list[SetMagnificationRequestOpticsItem]
    """The optics units to apply the change to."""


class SetRelativeMagnificationRequestOpticsItem(Model):
    optics_id: str = Field(validation_alias="opticsId", serialization_alias="opticsId")
    """The optics ID to change the relative magnification on."""
    type: RelativeStepType
    """The step size: +bigStep, -bigStep, +smallStep, -smallStep, or numerical to use value."""
    value: float | None = None
    """The desired magnification offset. Used when type is numerical."""


class SetRelativeMagnificationRequest(Model):
    optics: list[SetRelativeMagnificationRequestOpticsItem]
    """The optics units to apply the change to."""


class CalibrateRequestOpticsItem(Model):
    optics_id: str = Field(validation_alias="opticsId", serialization_alias="opticsId")
    """The optics ID to calibrate."""
    focus: bool | None = None
    """Whether to calibrate focus. Defaults to false."""
    zoom: bool | None = None
    """Whether to calibrate zoom. Defaults to false; ignored if the device has no zoom."""


class CalibrateRequest(Model):
    optics: list[CalibrateRequestOpticsItem]
    """The optics units to apply the change to."""


class PerformAutofocusRequestOpticsItem(Model):
    optics_id: str = Field(validation_alias="opticsId", serialization_alias="opticsId")
    """The optics ID to perform autofocus on."""


class PerformAutofocusRequest(Model):
    optics: list[PerformAutofocusRequestOpticsItem]
    """The optics units to apply the change to."""


class ResetRequestOpticsItem(Model):
    optics_id: str = Field(validation_alias="opticsId", serialization_alias="opticsId")
    """The optics ID to reset."""
    focus: bool | None = None
    """Whether to reset focus. Defaults to false."""
    zoom: bool | None = None
    """Whether to reset zoom. Defaults to false; ignored if the device has no zoom."""


class ResetRequest(Model):
    optics: list[ResetRequestOpticsItem]
    """The optics units to apply the change to."""


class SetFocusWindowRequestOpticsItem(Model):
    optics_id: str = Field(validation_alias="opticsId", serialization_alias="opticsId")
    """The optics ID to set the focus window on."""
    upper_left_x: float = Field(validation_alias="upperLeftX", serialization_alias="upperLeftX", ge=0, le=1)
    """Distance from the full image upper left corner to the window upper left corner along X, a fraction of the image width between 0 and 1."""
    upper_left_y: float = Field(validation_alias="upperLeftY", serialization_alias="upperLeftY", ge=0, le=1)
    """Distance from the full image upper left corner to the window upper left corner along Y, a fraction of the image height between 0 and 1."""
    width: float = Field(ge=0, le=1)
    """Window width, a fraction of the image width between 0 and 1. upperLeftX+width over 1 is truncated."""
    height: float = Field(ge=0, le=1)
    """Window height, a fraction of the image height between 0 and 1. upperLeftY+height over 1 is truncated."""


class SetFocusWindowRequest(Model):
    optics: list[SetFocusWindowRequestOpticsItem]
    """The optics units to apply the change to."""


class SetTemperatureCompensationRequestOpticsItem(Model):
    optics_id: str = Field(validation_alias="opticsId", serialization_alias="opticsId")
    """The optics ID to set temperature compensation on."""
    enable: bool
    """Whether active temperature compensation is enabled."""


class SetTemperatureCompensationRequest(Model):
    optics: list[SetTemperatureCompensationRequestOpticsItem]
    """The optics units to apply the change to."""


class SetIrCutFilterStateRequestOpticsItem(Model):
    optics_id: str = Field(validation_alias="opticsId", serialization_alias="opticsId")
    """The optics ID to set the IRCut filter on."""
    ir_cut_filter_state: IrCutFilterState = Field(
        validation_alias="irCutFilterState", serialization_alias="irCutFilterState"
    )
    """on: filter forced on. off: filter forced off. auto: decided by the software algorithm."""


class SetIrCutFilterStateRequest(Model):
    optics: list[SetIrCutFilterStateRequestOpticsItem]
    """The optics units to apply the change to."""


class SetIrCompensationRequestOpticsItem(Model):
    optics_id: str = Field(validation_alias="opticsId", serialization_alias="opticsId")
    """The optics ID to set the IR compensation on."""
    enable: bool
    """Whether active IR compensation is enabled."""


class SetIrCompensationRequest(Model):
    optics: list[SetIrCompensationRequestOpticsItem]
    """The optics units to apply the change to."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/opticscontrol.cgi"

INFO = ApiInfo(
    id="optics-control",
    name="Optics Control API",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 1), ApiVersion(1, 2)),
    discovery=(ApiDiscovery("optics-control"),),
    docs=("https://developer.axis.com/vapix/network-video/optics-control/",),
    errors={
        1100: ErrorCode("Internal error", "internal"),
        1200: ErrorCode("Temperature out of range", "unavailable"),
        1300: ErrorCode("Focus not found", "not_found"),
        2100: ErrorCode("API version not supported", "unsupported"),
        2101: ErrorCode("Invalid JSON", "invalid_argument"),
        2102: ErrorCode("Method not supported", "unsupported"),
        2103: ErrorCode("Required parameter missing", "invalid_argument"),
        2104: ErrorCode("Invalid parameter value specified", "invalid_argument"),
        2105: ErrorCode("Authorization failed", "access_denied"),
        2106: ErrorCode("Authentication failed", "access_denied"),
    },
)


class OPS:
    get_optics = Operation(
        INFO, "get_optics", JsonRpcBinding("getOptics", PATH), result=OpticsList, access="operator", effect="read"
    )
    get_capabilities = Operation(
        INFO,
        "get_capabilities",
        JsonRpcBinding("getCapabilities", PATH),
        result=CapabilitiesList,
        access="operator",
        effect="read",
    )
    set_focus = Operation(
        INFO,
        "set_focus",
        JsonRpcBinding("setFocus", PATH),
        params=SetFocusRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_relative_focus = Operation(
        INFO,
        "set_relative_focus",
        JsonRpcBinding("setRelativeFocus", PATH),
        params=SetRelativeFocusRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_magnification = Operation(
        INFO,
        "set_magnification",
        JsonRpcBinding("setMagnification", PATH),
        params=SetMagnificationRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_relative_magnification = Operation(
        INFO,
        "set_relative_magnification",
        JsonRpcBinding("setRelativeMagnification", PATH),
        params=SetRelativeMagnificationRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    calibrate = Operation(
        INFO, "calibrate", JsonRpcBinding("calibrate", PATH), params=CalibrateRequest, access="admin", effect="action"
    )
    perform_autofocus = Operation(
        INFO,
        "perform_autofocus",
        JsonRpcBinding("performAutofocus", PATH),
        params=PerformAutofocusRequest,
        access="admin",
        effect="action",
    )
    reset = Operation(
        INFO, "reset", JsonRpcBinding("reset", PATH), params=ResetRequest, access="admin", effect="action"
    )
    set_focus_window = Operation(
        INFO,
        "set_focus_window",
        JsonRpcBinding("setFocusWindow", PATH),
        params=SetFocusWindowRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_temperature_compensation = Operation(
        INFO,
        "set_temperature_compensation",
        JsonRpcBinding("setTemperatureCompensation", PATH),
        params=SetTemperatureCompensationRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_ir_cut_filter_state = Operation(
        INFO,
        "set_ir_cut_filter_state",
        JsonRpcBinding("setIrCutFilterState", PATH),
        params=SetIrCutFilterStateRequest,
        access="operator",
        effect="write",
        write="patch",
    )
    set_ir_compensation = Operation(
        INFO,
        "set_ir_compensation",
        JsonRpcBinding("setIrCompensation", PATH),
        params=SetIrCompensationRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class OpticsControlApi(SyncApi):
    """Optics Control API (``optics-control``, version 1)."""

    INFO = INFO

    def get_optics(self, *, request_options: RequestOptions | None = None) -> OpticsList:
        """Retrieves information about all available optics.

        This method retrieves all optics along with their status and abilities.

        Access: operator.
        """
        return self._run(OPS.get_optics, None, {}, request_options)

    def get_capabilities(self, *, request_options: RequestOptions | None = None) -> CapabilitiesList:
        """Retrieves information about the optics capabilities.

        This method retrieves the capabilities of all available optics.

        Access: operator.
        """
        return self._run(OPS.get_capabilities, None, {}, request_options)

    @overload
    def set_focus(self, request: SetFocusRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def set_focus(
        self, /, *, optics: list[SetFocusRequestOpticsItem], request_options: RequestOptions | None = None
    ) -> None: ...
    def set_focus(
        self, request: SetFocusRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Sets a focus position on one or more of the optics.

        This method sets a focus position for one or more optics.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_focus, request, kwargs, request_options)

    @overload
    def set_relative_focus(
        self, request: SetRelativeFocusRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_relative_focus(
        self, /, *, optics: list[SetRelativeFocusRequestOpticsItem], request_options: RequestOptions | None = None
    ) -> None: ...
    def set_relative_focus(
        self,
        request: SetRelativeFocusRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Changes the focus relative to the current position on one or more optics.

        This method changes the current focus with relative focus movement.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_relative_focus, request, kwargs, request_options)

    @overload
    def set_magnification(
        self, request: SetMagnificationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_magnification(
        self, /, *, optics: list[SetMagnificationRequestOpticsItem], request_options: RequestOptions | None = None
    ) -> None: ...
    def set_magnification(
        self,
        request: SetMagnificationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Sets a magnification on one or more of the optics.

        This method sets the magnification for one or more optics. Please note that this is only available
        on products with the capability zoom. See [getCapabilities](#getcapabilities) to find out if your
        product supports specific capabilities.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_magnification, request, kwargs, request_options)

    @overload
    def set_relative_magnification(
        self, request: SetRelativeMagnificationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_relative_magnification(
        self,
        /,
        *,
        optics: list[SetRelativeMagnificationRequestOpticsItem],
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_relative_magnification(
        self,
        request: SetRelativeMagnificationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Changes the magnification relative to the current position on one or more optics.

        This method changes the current magnification with relative magnification movement.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_relative_magnification, request, kwargs, request_options)

    @overload
    def calibrate(self, request: CalibrateRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def calibrate(
        self, /, *, optics: list[CalibrateRequestOpticsItem], request_options: RequestOptions | None = None
    ) -> None: ...
    def calibrate(
        self,
        request: CalibrateRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Calibrates the optics.

        This method calibrates the optics for both zoom and focus, which is useful for optics that ended up
        in an undefined state and needs a re-calibration. This is only available on devices where either
        `calibrateFocus` or `calibrateZoom` is present.

        Access: admin.
        """
        self._run(OPS.calibrate, request, kwargs, request_options)

    @overload
    def perform_autofocus(
        self, request: PerformAutofocusRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def perform_autofocus(
        self, /, *, optics: list[PerformAutofocusRequestOpticsItem], request_options: RequestOptions | None = None
    ) -> None: ...
    def perform_autofocus(
        self,
        request: PerformAutofocusRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Starts an automatic focus search. Access: admin."""
        self._run(OPS.perform_autofocus, request, kwargs, request_options)

    @overload
    def reset(self, request: ResetRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def reset(
        self, /, *, optics: list[ResetRequestOpticsItem], request_options: RequestOptions | None = None
    ) -> None: ...
    def reset(
        self, request: ResetRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Resets the optics back to their default position.

        This method resets the optics back to their default position.

        Access: admin.
        """
        self._run(OPS.reset, request, kwargs, request_options)

    @overload
    def set_focus_window(
        self, request: SetFocusWindowRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_focus_window(
        self, /, *, optics: list[SetFocusWindowRequestOpticsItem], request_options: RequestOptions | None = None
    ) -> None: ...
    def set_focus_window(
        self,
        request: SetFocusWindowRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Sets the window in which autofocus will optimize the focus.

        This method sets the window where the automatic focus search should optimize the focus.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_focus_window, request, kwargs, request_options)

    @overload
    def set_temperature_compensation(
        self, request: SetTemperatureCompensationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_temperature_compensation(
        self,
        /,
        *,
        optics: list[SetTemperatureCompensationRequestOpticsItem],
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def set_temperature_compensation(
        self,
        request: SetTemperatureCompensationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Sets the state for the active temperature compensation.

        This method sets the active temperature compensation that should be used. This method is only
        available if `compensateTemperature` is true. Please note that the active focus compensation might
        not work as well if your device has a non-standard lens.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_temperature_compensation, request, kwargs, request_options)

    @overload
    def set_ir_cut_filter_state(
        self, request: SetIrCutFilterStateRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_ir_cut_filter_state(
        self, /, *, optics: list[SetIrCutFilterStateRequestOpticsItem], request_options: RequestOptions | None = None
    ) -> None: ...
    def set_ir_cut_filter_state(
        self,
        request: SetIrCutFilterStateRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Sets the state for the IRCut filter.

        This method sets the desired state of the IRCut filter to either `on/off/auto`. The settings `on`
        and `off` reflect the manual state while `auto` leaves the decision of the IRCut filter state to the
        software algorithms.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_ir_cut_filter_state, request, kwargs, request_options)

    @overload
    def set_ir_compensation(
        self, request: SetIrCompensationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_ir_compensation(
        self, /, *, optics: list[SetIrCompensationRequestOpticsItem], request_options: RequestOptions | None = None
    ) -> None: ...
    def set_ir_compensation(
        self,
        request: SetIrCompensationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Sets the state for the active IR compensation.

        This method decides if IR compensation should be used.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_ir_compensation, request, kwargs, request_options)


class AsyncOpticsControlApi(AsyncApi):
    """Optics Control API (``optics-control``, version 1)."""

    INFO = INFO

    async def get_optics(self, *, request_options: RequestOptions | None = None) -> OpticsList:
        """Retrieves information about all available optics.

        This method retrieves all optics along with their status and abilities.

        Access: operator.
        """
        return await self._run(OPS.get_optics, None, {}, request_options)

    async def get_capabilities(self, *, request_options: RequestOptions | None = None) -> CapabilitiesList:
        """Retrieves information about the optics capabilities.

        This method retrieves the capabilities of all available optics.

        Access: operator.
        """
        return await self._run(OPS.get_capabilities, None, {}, request_options)

    @overload
    async def set_focus(
        self, request: SetFocusRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_focus(
        self, /, *, optics: list[SetFocusRequestOpticsItem], request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_focus(
        self, request: SetFocusRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Sets a focus position on one or more of the optics.

        This method sets a focus position for one or more optics.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_focus, request, kwargs, request_options)

    @overload
    async def set_relative_focus(
        self, request: SetRelativeFocusRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_relative_focus(
        self, /, *, optics: list[SetRelativeFocusRequestOpticsItem], request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_relative_focus(
        self,
        request: SetRelativeFocusRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Changes the focus relative to the current position on one or more optics.

        This method changes the current focus with relative focus movement.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_relative_focus, request, kwargs, request_options)

    @overload
    async def set_magnification(
        self, request: SetMagnificationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_magnification(
        self, /, *, optics: list[SetMagnificationRequestOpticsItem], request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_magnification(
        self,
        request: SetMagnificationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Sets a magnification on one or more of the optics.

        This method sets the magnification for one or more optics. Please note that this is only available
        on products with the capability zoom. See [getCapabilities](#getcapabilities) to find out if your
        product supports specific capabilities.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_magnification, request, kwargs, request_options)

    @overload
    async def set_relative_magnification(
        self, request: SetRelativeMagnificationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_relative_magnification(
        self,
        /,
        *,
        optics: list[SetRelativeMagnificationRequestOpticsItem],
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_relative_magnification(
        self,
        request: SetRelativeMagnificationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Changes the magnification relative to the current position on one or more optics.

        This method changes the current magnification with relative magnification movement.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_relative_magnification, request, kwargs, request_options)

    @overload
    async def calibrate(
        self, request: CalibrateRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def calibrate(
        self, /, *, optics: list[CalibrateRequestOpticsItem], request_options: RequestOptions | None = None
    ) -> None: ...
    async def calibrate(
        self,
        request: CalibrateRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Calibrates the optics.

        This method calibrates the optics for both zoom and focus, which is useful for optics that ended up
        in an undefined state and needs a re-calibration. This is only available on devices where either
        `calibrateFocus` or `calibrateZoom` is present.

        Access: admin.
        """
        await self._run(OPS.calibrate, request, kwargs, request_options)

    @overload
    async def perform_autofocus(
        self, request: PerformAutofocusRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def perform_autofocus(
        self, /, *, optics: list[PerformAutofocusRequestOpticsItem], request_options: RequestOptions | None = None
    ) -> None: ...
    async def perform_autofocus(
        self,
        request: PerformAutofocusRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Starts an automatic focus search. Access: admin."""
        await self._run(OPS.perform_autofocus, request, kwargs, request_options)

    @overload
    async def reset(self, request: ResetRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    async def reset(
        self, /, *, optics: list[ResetRequestOpticsItem], request_options: RequestOptions | None = None
    ) -> None: ...
    async def reset(
        self, request: ResetRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> None:
        """Resets the optics back to their default position.

        This method resets the optics back to their default position.

        Access: admin.
        """
        await self._run(OPS.reset, request, kwargs, request_options)

    @overload
    async def set_focus_window(
        self, request: SetFocusWindowRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_focus_window(
        self, /, *, optics: list[SetFocusWindowRequestOpticsItem], request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_focus_window(
        self,
        request: SetFocusWindowRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Sets the window in which autofocus will optimize the focus.

        This method sets the window where the automatic focus search should optimize the focus.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_focus_window, request, kwargs, request_options)

    @overload
    async def set_temperature_compensation(
        self, request: SetTemperatureCompensationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_temperature_compensation(
        self,
        /,
        *,
        optics: list[SetTemperatureCompensationRequestOpticsItem],
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def set_temperature_compensation(
        self,
        request: SetTemperatureCompensationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Sets the state for the active temperature compensation.

        This method sets the active temperature compensation that should be used. This method is only
        available if `compensateTemperature` is true. Please note that the active focus compensation might
        not work as well if your device has a non-standard lens.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_temperature_compensation, request, kwargs, request_options)

    @overload
    async def set_ir_cut_filter_state(
        self, request: SetIrCutFilterStateRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_ir_cut_filter_state(
        self, /, *, optics: list[SetIrCutFilterStateRequestOpticsItem], request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_ir_cut_filter_state(
        self,
        request: SetIrCutFilterStateRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Sets the state for the IRCut filter.

        This method sets the desired state of the IRCut filter to either `on/off/auto`. The settings `on`
        and `off` reflect the manual state while `auto` leaves the decision of the IRCut filter state to the
        software algorithms.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_ir_cut_filter_state, request, kwargs, request_options)

    @overload
    async def set_ir_compensation(
        self, request: SetIrCompensationRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_ir_compensation(
        self, /, *, optics: list[SetIrCompensationRequestOpticsItem], request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_ir_compensation(
        self,
        request: SetIrCompensationRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Sets the state for the active IR compensation.

        This method decides if IR compensation should be used.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_ir_compensation, request, kwargs, request_options)
