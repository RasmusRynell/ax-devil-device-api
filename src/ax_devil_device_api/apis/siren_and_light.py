# GENERATED from specs/apis/network-video/siren-and-light.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Control the siren and light of a device with patterns, priorities and profiles; run a health check and set maintenance mode.

Docs: https://developer.axis.com/vapix/network-video/siren-and-light/
"""

from __future__ import annotations

from typing import Any, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class Duration(Model):
    """How long a pattern runs."""

    unit: Literal["seconds", "repetitions"]
    """Duration unit."""
    value: int = Field(ge=0, le=259200)
    """Duration value. Valid ranges 0-259200 for seconds and 0-20 for repetitions."""


class SirenConfig(Model):
    """Siren settings of a start request or a profile."""

    pattern: str
    """Name of the siren pattern (see get_capabilities)."""
    intensity: int | None = None
    """Siren intensity level."""
    duration: Duration | None = None
    priority: int | None = None
    """Priority level. 1 to 10 for users; 11 and above are reserved for service functions."""


class LightConfig(Model):
    """Light settings of a start request or a profile."""

    pattern: str
    """Name of the light pattern. Must be supplied if a light is used."""
    speed: int | None = None
    """Speed for the light pattern."""
    colors: list[str] | None = None
    """Color names, e.g. red, green, blue, amber, white."""
    intensity: int | None = None
    """Light intensity level."""
    duration: Duration | None = None
    priority: int | None = None
    """Priority level."""


class Profile(Model):
    """A stored combination of siren and light settings."""

    name: str = Field(max_length=50)
    """Unique profile name (identifier), max 50 characters."""
    description: str | None = Field(default=None, max_length=250)
    """User description, max 250 characters."""
    siren: SirenConfig | None = None
    light: LightConfig | None = None


class PoeIntensity(Model):
    possible: list[int] | None = None
    """Supported intensity levels for this PoE class."""
    default: int | None = None
    """Intensity used when the pattern is started without one."""


class IntensityCapability(Model):
    poe_class: dict[str, PoeIntensity] | None = Field(
        default=None, validation_alias="poeClass", serialization_alias="poeClass"
    )
    """Intensity properties keyed by PoE class ("3", "4"). Contains the PoE class the device supports."""


class PriorityCapability(Model):
    possible: list[int] | None = None
    """Supported priority levels."""
    default: int | None = None
    """Priority used when the pattern is started without one."""


class SirenPatternCapability(Model):
    name: str | None = None
    """Siren pattern name."""
    intensity: IntensityCapability | None = None
    priority: PriorityCapability | None = None


class SpeedCapability(Model):
    possible: list[int] | None = None
    default: int | None = None
    """Speed used when not set."""


class ColorCapability(Model):
    min_nbr_colors: int | None = Field(
        default=None, validation_alias="minNbrColors", serialization_alias="minNbrColors"
    )
    """Minimum number of different colors the pattern needs."""
    max_nbr_colors: int | None = Field(
        default=None, validation_alias="maxNbrColors", serialization_alias="maxNbrColors"
    )
    """Maximum number of colors; the maximum length of the colors array at start."""
    possible: list[str] | None = None
    """Names of the colors the pattern can flash in."""
    default: list[str] | None = None
    """Colors used when the pattern is started without any."""


class LightPatternCapability(Model):
    name: str | None = None
    """Light pattern name."""
    speed: SpeedCapability | None = None
    colors: ColorCapability | None = None
    intensity: IntensityCapability | None = None
    priority: PriorityCapability | None = None


class SirenCapabilities(Model):
    supported_patterns: list[SirenPatternCapability] | None = Field(
        default=None, validation_alias="supportedPatterns", serialization_alias="supportedPatterns"
    )


class LightCapabilities(Model):
    supported_patterns: list[LightPatternCapability] | None = Field(
        default=None, validation_alias="supportedPatterns", serialization_alias="supportedPatterns"
    )


class Capabilities(Model):
    siren: SirenCapabilities | None = None
    light: LightCapabilities | None = None
    health_check_support: bool | None = Field(
        default=None, validation_alias="healthCheckSupport", serialization_alias="healthCheckSupport"
    )
    """Whether the service supports health check."""
    maintenance_mode_support: bool | None = Field(
        default=None, validation_alias="maintenanceModeSupport", serialization_alias="maintenanceModeSupport"
    )
    """Whether the service supports maintenance mode."""
    poe_class: str | None = Field(default=None, validation_alias="poeClass", serialization_alias="poeClass")
    """The current PoE class."""


class CapabilitiesResult(Model):
    capabilities: Capabilities


class SirenStatus(Model):
    """A running siren operation."""

    siren_id: int | str | None = Field(default=None, validation_alias="sirenId", serialization_alias="sirenId")
    """Siren ID. Documented as a string; the examples show an integer."""
    pattern: str | None = None
    """Running pattern name."""
    intensity: int | None = None
    """Running intensity level."""
    duration_left: int | None = Field(default=None, validation_alias="durationLeft", serialization_alias="durationLeft")
    """Seconds left until stop; decreases even when other higher-priority patterns are active."""
    priority: int | None = None
    """Priority used to start the pattern."""
    profile: str | None = None
    """Name of the running profile."""


class LightStatus(Model):
    """A running light operation."""

    light_id: int | str | None = Field(default=None, validation_alias="lightId", serialization_alias="lightId")
    """Light ID. Documented as a string; the examples show an integer."""
    speed: int | None = None
    """Speed of running light pattern."""
    colors: list[str] | None = None
    pattern: str | None = None
    """Running pattern name."""
    intensity: int | None = None
    """Running intensity level."""
    duration_left: int | None = Field(default=None, validation_alias="durationLeft", serialization_alias="durationLeft")
    """Seconds left until stop; decreases even when other higher-priority patterns are active."""
    priority: int | None = None
    """Priority used to start the pattern."""
    profile: str | None = None
    """Name of the running profile."""


class Status(Model):
    siren: list[SirenStatus] | None = None
    light: list[LightStatus] | None = None


class ProfileList(Model):
    profiles: list[Profile] | None = None


class StartRequest(Model):
    """Arguments of ``start``. Use either ``profile`` or ``siren`` and ``light``, not both."""

    siren: SirenConfig | None = None
    """Siren properties. Cannot be used together with profile."""
    light: LightConfig | None = None
    """Light properties. Cannot be used together with profile."""
    profile: str | None = None
    """Profile name. Cannot be used together with siren or light."""


class StartResult(Model):
    siren_id: int | None = Field(default=None, validation_alias="sirenId", serialization_alias="sirenId")
    """Siren operation ID (handle for stop)."""
    light_id: int | None = Field(default=None, validation_alias="lightId", serialization_alias="lightId")
    """Light operation ID (handle for stop)."""


class StopRequest(Model):
    """Arguments of ``stop``. Give sirenId and/or lightId, ``all``, or ``profile``."""

    siren_id: int | None = Field(default=None, validation_alias="sirenId", serialization_alias="sirenId")
    """ID handle of the siren operation."""
    light_id: int | None = Field(default=None, validation_alias="lightId", serialization_alias="lightId")
    """ID handle of the light operation."""
    all: list[Literal["siren", "light"]] | None = None
    """Types to stop; may stop multiple requests with different priorities."""
    profile: str | None = None
    """Profile name whose operations to stop."""


class AddProfileRequest(Model):
    """Arguments of ``add_profile``."""

    name: str = Field(max_length=50)
    """Unique profile name, max 50 characters."""
    description: str | None = Field(default=None, max_length=250)
    """Max 250 characters."""
    siren: SirenConfig | None = None
    """Siren configuration."""
    light: LightConfig | None = None
    """Light configuration."""


class RemoveProfileRequest(Model):
    name: str
    """Name of the profile to remove."""


class HealthCheckError(Model):
    code: int | None = None
    """Health check error code."""
    message: str | None = None
    """Description of the error."""


class HealthCheckResult(Model):
    timestamp: str | None = None
    """ISO 8601 timestamp of the latest health check. (format=date-time)"""
    errors: list[HealthCheckError] | None = None


class SetMaintenanceModeRequest(Model):
    maintenance_mode: bool = Field(validation_alias="maintenanceMode", serialization_alias="maintenanceMode")
    """true engages, false disengages."""
    duration: int | None = None
    """Seconds the maintenance mode is active when true. (unit=s)"""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/siren_and_light.cgi"

INFO = ApiInfo(
    id="siren-and-light",
    name="Siren and light",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(ApiDiscovery("siren-and-light"),),
    docs=("https://developer.axis.com/vapix/network-video/siren-and-light/",),
    errors={
        1100: ErrorCode("Internal error", "internal"),
        1200: ErrorCode("Service is not initialized", "unavailable"),
        1201: ErrorCode("Maximum number of profiles reached"),
        1202: ErrorCode("Requested profile is invalid", "invalid_argument"),
        1203: ErrorCode("Requested process id does not exist", "not_found"),
        1204: ErrorCode("Service does not support health check", "unsupported"),
        1205: ErrorCode("Service does not support maintenance mode", "unsupported"),
        2100: ErrorCode("The API version is not supported", "unsupported"),
        2101: ErrorCode("Invalid JSON", "invalid_argument"),
        2102: ErrorCode("Method not supported", "unsupported"),
        2103: ErrorCode("Required parameter missing", "invalid_argument"),
        2104: ErrorCode("Invalid parameter value specified", "invalid_argument"),
        2200: ErrorCode("Requested siren pattern is invalid", "invalid_argument"),
        2201: ErrorCode("Requested light pattern is invalid", "invalid_argument"),
        2202: ErrorCode("Requested siren intensity is invalid", "invalid_argument"),
        2203: ErrorCode("Requested light intensity is invalid", "invalid_argument"),
        2204: ErrorCode("Requested siren priority is invalid", "invalid_argument"),
        2205: ErrorCode("Requested light priority is invalid", "invalid_argument"),
        2206: ErrorCode("Requested siren duration unit is invalid", "invalid_argument"),
        2207: ErrorCode("Requested light duration unit is invalid", "invalid_argument"),
        2208: ErrorCode("Requested siren duration is invalid", "invalid_argument"),
        2209: ErrorCode("Requested light duration is invalid", "invalid_argument"),
        2210: ErrorCode("Requested function type is invalid", "invalid_argument"),
        2211: ErrorCode("Requested number of colors is invalid", "invalid_argument"),
        2212: ErrorCode("Requested color is invalid", "invalid_argument"),
        2213: ErrorCode("Profile name is too long", "invalid_argument"),
        2214: ErrorCode("Description is too long", "invalid_argument"),
        2215: ErrorCode("Requested speed is invalid", "invalid_argument"),
    },
)


class OPS:
    get_capabilities = Operation(
        INFO,
        "get_capabilities",
        JsonRpcBinding("getCapabilities", PATH),
        result=CapabilitiesResult,
        access="operator",
        effect="read",
    )
    get_status = Operation(
        INFO, "get_status", JsonRpcBinding("getStatus", PATH), result=Status, access="operator", effect="read"
    )
    get_profiles = Operation(
        INFO, "get_profiles", JsonRpcBinding("getProfiles", PATH), result=ProfileList, access="operator", effect="read"
    )
    start = Operation(
        INFO,
        "start",
        JsonRpcBinding("start", PATH),
        params=StartRequest,
        result=StartResult,
        access="operator",
        effect="action",
    )
    stop = Operation(INFO, "stop", JsonRpcBinding("stop", PATH), params=StopRequest, access="operator", effect="action")
    add_profile = Operation(
        INFO,
        "add_profile",
        JsonRpcBinding("addProfile", PATH),
        params=AddProfileRequest,
        access="operator",
        effect="write",
        write="create",
    )
    remove_profile = Operation(
        INFO,
        "remove_profile",
        JsonRpcBinding("removeProfile", PATH),
        params=RemoveProfileRequest,
        access="operator",
        effect="write",
        write="delete",
    )
    run_health_check = Operation(
        INFO, "run_health_check", JsonRpcBinding("runHealthCheck", PATH), access="operator", effect="action"
    )
    get_last_health_check = Operation(
        INFO,
        "get_last_health_check",
        JsonRpcBinding("getLastHealthCheck", PATH),
        result=HealthCheckResult,
        access="operator",
        effect="read",
    )
    set_maintenance_mode = Operation(
        INFO,
        "set_maintenance_mode",
        JsonRpcBinding("setMaintenanceMode", PATH),
        params=SetMaintenanceModeRequest,
        access="operator",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class SirenAndLightApi(SyncApi):
    """Siren and light (``siren-and-light``, version 1)."""

    INFO = INFO

    def get_capabilities(self, *, request_options: RequestOptions | None = None) -> CapabilitiesResult:
        """List the supported services (siren, light) and their capabilities.

        Patterns, intensities per PoE class, priorities, speeds and colors. Pattern and color names are
        device dependent.

        Access: operator.
        """
        return self._run(OPS.get_capabilities, None, {}, request_options)

    def get_status(self, *, request_options: RequestOptions | None = None) -> Status:
        """List the current status (running operations) of siren and light.

        Priorities 11 and above are reserved for service functions: Maintenance mode 11, Find my device 12,
        Health check 13.

        Access: operator.
        """
        return self._run(OPS.get_status, None, {}, request_options)

    def get_profiles(self, *, request_options: RequestOptions | None = None) -> ProfileList:
        """List the registered profiles. Access: operator."""
        return self._run(OPS.get_profiles, None, {}, request_options)

    @overload
    def start(self, request: StartRequest, /, *, request_options: RequestOptions | None = None) -> StartResult: ...
    @overload
    def start(
        self,
        /,
        *,
        siren: SirenConfig | MISSING = MISSING,
        light: LightConfig | MISSING = MISSING,
        profile: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> StartResult: ...
    def start(
        self, request: StartRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> StartResult:
        """Start the siren and/or light, from explicit settings or a profile.

        Depending on state and priority the operation is active or stored to be activated later. The highest
        priority operation runs; runtime of inactive operations still decreases. Only one operation per
        priority level is stored; start with an identical priority to replace it.

        Access: operator.
        """
        return self._run(OPS.start, request, kwargs, request_options)

    def stop(
        self,
        *,
        siren_id: int | MISSING = MISSING,
        light_id: int | MISSING = MISSING,
        all: list[Literal["siren", "light"]] | MISSING = MISSING,
        profile: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Stop running operations: all of a type, one siren/light operation by ID, or those started by a profile.

        Stopping by sirenId/lightId also initiates operations with lower priorities.

        Access: operator.
        """
        self._run(
            OPS.stop,
            None,
            {"siren_id": siren_id, "light_id": light_id, "all": all, "profile": profile},
            request_options,
        )

    @overload
    def add_profile(self, request: AddProfileRequest, /, *, request_options: RequestOptions | None = None) -> None: ...
    @overload
    def add_profile(
        self,
        /,
        *,
        name: str,
        description: str | MISSING = MISSING,
        siren: SirenConfig | MISSING = MISSING,
        light: LightConfig | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    def add_profile(
        self,
        request: AddProfileRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Add a new profile. Access: operator."""
        self._run(OPS.add_profile, request, kwargs, request_options)

    def remove_profile(self, name: str, *, request_options: RequestOptions | None = None) -> None:
        """Remove an existing profile. Access: operator."""
        self._run(OPS.remove_profile, None, {"name": name}, request_options)

    def run_health_check(self, *, request_options: RequestOptions | None = None) -> None:
        """Start a health check; fetch the result later with get_last_health_check.

        The check takes some time.

        Access: operator.
        """
        self._run(OPS.run_health_check, None, {}, request_options)

    def get_last_health_check(self, *, request_options: RequestOptions | None = None) -> HealthCheckResult:
        """Retrieve the result of the latest completed health check. Access: operator."""
        return self._run(OPS.get_last_health_check, None, {}, request_options)

    def set_maintenance_mode(
        self,
        maintenance_mode: bool,
        *,
        duration: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Engage or disengage maintenance mode (a safe approach without alarm).

        The mode persists through a reboot.

        Changes only the fields given. Access: operator.
        """
        self._run(
            OPS.set_maintenance_mode,
            None,
            {"maintenance_mode": maintenance_mode, "duration": duration},
            request_options,
        )


class AsyncSirenAndLightApi(AsyncApi):
    """Siren and light (``siren-and-light``, version 1)."""

    INFO = INFO

    async def get_capabilities(self, *, request_options: RequestOptions | None = None) -> CapabilitiesResult:
        """List the supported services (siren, light) and their capabilities.

        Patterns, intensities per PoE class, priorities, speeds and colors. Pattern and color names are
        device dependent.

        Access: operator.
        """
        return await self._run(OPS.get_capabilities, None, {}, request_options)

    async def get_status(self, *, request_options: RequestOptions | None = None) -> Status:
        """List the current status (running operations) of siren and light.

        Priorities 11 and above are reserved for service functions: Maintenance mode 11, Find my device 12,
        Health check 13.

        Access: operator.
        """
        return await self._run(OPS.get_status, None, {}, request_options)

    async def get_profiles(self, *, request_options: RequestOptions | None = None) -> ProfileList:
        """List the registered profiles. Access: operator."""
        return await self._run(OPS.get_profiles, None, {}, request_options)

    @overload
    async def start(
        self, request: StartRequest, /, *, request_options: RequestOptions | None = None
    ) -> StartResult: ...
    @overload
    async def start(
        self,
        /,
        *,
        siren: SirenConfig | MISSING = MISSING,
        light: LightConfig | MISSING = MISSING,
        profile: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> StartResult: ...
    async def start(
        self, request: StartRequest | None = None, /, *, request_options: RequestOptions | None = None, **kwargs: Any
    ) -> StartResult:
        """Start the siren and/or light, from explicit settings or a profile.

        Depending on state and priority the operation is active or stored to be activated later. The highest
        priority operation runs; runtime of inactive operations still decreases. Only one operation per
        priority level is stored; start with an identical priority to replace it.

        Access: operator.
        """
        return await self._run(OPS.start, request, kwargs, request_options)

    async def stop(
        self,
        *,
        siren_id: int | MISSING = MISSING,
        light_id: int | MISSING = MISSING,
        all: list[Literal["siren", "light"]] | MISSING = MISSING,
        profile: str | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Stop running operations: all of a type, one siren/light operation by ID, or those started by a profile.

        Stopping by sirenId/lightId also initiates operations with lower priorities.

        Access: operator.
        """
        await self._run(
            OPS.stop,
            None,
            {"siren_id": siren_id, "light_id": light_id, "all": all, "profile": profile},
            request_options,
        )

    @overload
    async def add_profile(
        self, request: AddProfileRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def add_profile(
        self,
        /,
        *,
        name: str,
        description: str | MISSING = MISSING,
        siren: SirenConfig | MISSING = MISSING,
        light: LightConfig | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None: ...
    async def add_profile(
        self,
        request: AddProfileRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Add a new profile. Access: operator."""
        await self._run(OPS.add_profile, request, kwargs, request_options)

    async def remove_profile(self, name: str, *, request_options: RequestOptions | None = None) -> None:
        """Remove an existing profile. Access: operator."""
        await self._run(OPS.remove_profile, None, {"name": name}, request_options)

    async def run_health_check(self, *, request_options: RequestOptions | None = None) -> None:
        """Start a health check; fetch the result later with get_last_health_check.

        The check takes some time.

        Access: operator.
        """
        await self._run(OPS.run_health_check, None, {}, request_options)

    async def get_last_health_check(self, *, request_options: RequestOptions | None = None) -> HealthCheckResult:
        """Retrieve the result of the latest completed health check. Access: operator."""
        return await self._run(OPS.get_last_health_check, None, {}, request_options)

    async def set_maintenance_mode(
        self,
        maintenance_mode: bool,
        *,
        duration: int | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Engage or disengage maintenance mode (a safe approach without alarm).

        The mode persists through a reboot.

        Changes only the fields given. Access: operator.
        """
        await self._run(
            OPS.set_maintenance_mode,
            None,
            {"maintenance_mode": maintenance_mode, "duration": duration},
            request_options,
        )
