# GENERATED from specs/apis/device-configuration/autopilot-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""The VAPIX® Autopilot API makes it possible to configure the PTZ camera's autopilot.

Docs: https://developer.axis.com/vapix/device-configuration/autopilot-api/
"""

from __future__ import annotations

from typing import Annotated, Any, ClassVar, Literal, overload

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

AutopilotState = Literal[
    "autotuneFailed",
    "autotuneRetry",
    "autotuning",
    "calibrationNeeded",
    "checkCalibration",
    "checkCalibrationRemoteConnection",
    "checkCalibrationRemoteConnectionFailed",
    "checkZoom",
    "checkZoomFailed",
    "connectToPtz",
    "connectToPtzFailed",
    "disabled",
    "gotoStartPosition",
    "gotoStartPositionFailed",
    "paused",
    "running",
    "soloMode",
    "soloModeError",
    "start",
    "startCalibration",
    "waitingForPtz",
]
CalibrationStatus = Literal["uncalibrated", "calibrated", "calibrating", "calibrationFailed"]
ChannelId = int


class ChannelCalibrated(Model):
    """Data if a channel is calibrated to the connected remote PTZ."""

    calibrated: bool | None = None
    """If the channel is calibrated."""
    channel_id: ChannelId | None = Field(default=None, validation_alias="channelId", serialization_alias="channelId")
    """The channel ID."""


ChannelsCalibrated = list[ChannelCalibrated]
ObjectSwitchTime = Annotated[int, Field(ge=0, le=60)]
ScenarioPriority = Annotated[int, Field(ge=1, le=20)]
ScenarioId = int


class ScenarioData(Model):
    """Data to configure a scenario."""

    channel_id: ChannelId | None = Field(default=None, validation_alias="channelId", serialization_alias="channelId")
    """Channel Id to which the scenario corresponds to."""
    enabled: bool | None = None
    """Enable tracking for the scenario."""
    priority: ScenarioPriority | None = None
    """Priority of the scenario, higher values signifies higher priority."""
    scenario_id: ScenarioId | None = Field(
        default=None, validation_alias="scenarioId", serialization_alias="scenarioId"
    )
    """Scenario Id to which the scenario corresponds to."""


ScenariosData = list[ScenarioData]


class Calibration(Model):
    """Control the calibration process."""

    __read_only__: ClassVar[frozenset[str]] = frozenset({"channels_calibrated", "status"})
    channels_calibrated: ChannelsCalibrated | None = Field(
        default=None, validation_alias="channelsCalibrated", serialization_alias="channelsCalibrated"
    )
    """Get a list of channels IDs and if they are calibrated to the remote PTZ."""
    status: CalibrationStatus | None = None
    """Get the current calibration status."""


class ObjectSwitch(Model):
    """Configure object switch for the Autopilot. This enables the Autopilot to switch tracking between objects, with a fixed time."""

    enabled: bool | None = None
    """Enable object switching on or off."""
    time: ObjectSwitchTime | None = None
    """Change the object switching time."""


class ScenarioConfiguration(Model):
    """Configure the scenarios."""

    scenarios: ScenariosData | None = None
    """Scenarios that configures which objects to track."""


class Autopilot(Model):
    """The whole API tree."""

    __read_only__: ClassVar[frozenset[str]] = frozenset({"in_solo_mode", "state"})
    enabled: bool | None = None
    """Turn on or off the Autopilot."""
    in_solo_mode: bool | None = Field(default=None, validation_alias="inSoloMode", serialization_alias="inSoloMode")
    """Get if the Autopilot is in solo mode, i.e. when there is no connected remote PTZ."""
    state: AutopilotState | None = None
    """Get the current state of Autopilot."""
    calibration: Calibration | None = None
    object_switch: ObjectSwitch | None = Field(
        default=None, validation_alias="objectSwitch", serialization_alias="objectSwitch"
    )
    scenario_configuration: ScenarioConfiguration | None = Field(
        default=None, validation_alias="scenarioConfiguration", serialization_alias="scenarioConfiguration"
    )


class UpdateAllRequest(Model):
    """Arguments of ``update_all``."""

    enabled: bool | None = None
    """Turn on or off the Autopilot."""


class UpdateObjectSwitchRequest(Model):
    """Arguments of ``update_object_switch``."""

    enabled: bool | None = None
    """Enable object switching on or off."""
    time: ObjectSwitchTime | None = None
    """Change the object switching time."""


class SetEnabledRequest(Model):
    enabled: bool
    """Turn on or off the Autopilot."""


class SetObjectSwitchEnabledRequest(Model):
    enabled: bool
    """Enable object switching on or off."""


class SetObjectSwitchTimeRequest(Model):
    time: ObjectSwitchTime
    """Change the object switching time."""


class SetScenarioConfigurationScenariosRequest(Model):
    scenarios: ScenariosData
    """Scenarios that configures which objects to track."""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/autopilot/v1"

INFO = ApiInfo(
    id="autopilot-config",
    name="Autopilot API",
    family=Family.DCA,
    discovery=(DcaDiscovery("autopilot", "v1"),),
    docs=("https://developer.axis.com/vapix/device-configuration/autopilot-api/",),
)


class OPS:
    get_all = Operation(INFO, "get_all", DcaBinding("GET", ROOT), result=Autopilot, access="admin", effect="read")
    update_all = Operation(
        INFO,
        "update_all",
        DcaBinding("PATCH", ROOT, body="object"),
        params=UpdateAllRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_enabled = Operation(
        INFO,
        "set_enabled",
        DcaBinding("PATCH", f"{ROOT}/enabled", body="value", body_field="enabled"),
        params=SetEnabledRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_in_solo_mode = Operation(
        INFO, "get_in_solo_mode", DcaBinding("GET", f"{ROOT}/inSoloMode"), result=bool, access="admin", effect="read"
    )
    get_state = Operation(
        INFO, "get_state", DcaBinding("GET", f"{ROOT}/state"), result=AutopilotState, access="admin", effect="read"
    )
    get_calibration = Operation(
        INFO,
        "get_calibration",
        DcaBinding("GET", f"{ROOT}/calibration"),
        result=Calibration,
        access="admin",
        effect="read",
    )
    get_calibration_status = Operation(
        INFO,
        "get_calibration_status",
        DcaBinding("GET", f"{ROOT}/calibration/status"),
        result=CalibrationStatus,
        access="admin",
        effect="read",
    )
    get_channels_calibrated = Operation(
        INFO,
        "get_channels_calibrated",
        DcaBinding("GET", f"{ROOT}/calibration/channelsCalibrated"),
        result=ChannelsCalibrated,
        access="admin",
        effect="read",
    )
    abort_calibration = Operation(
        INFO, "abort_calibration", DcaBinding("POST", f"{ROOT}/calibration/abort"), access="admin", effect="action"
    )
    start_calibration = Operation(
        INFO,
        "start_calibration",
        DcaBinding("POST", f"{ROOT}/calibration/start", body="object"),
        access="admin",
        effect="action",
    )
    get_object_switch = Operation(
        INFO,
        "get_object_switch",
        DcaBinding("GET", f"{ROOT}/objectSwitch"),
        result=ObjectSwitch,
        access="admin",
        effect="read",
    )
    update_object_switch = Operation(
        INFO,
        "update_object_switch",
        DcaBinding("PATCH", f"{ROOT}/objectSwitch", body="object"),
        params=UpdateObjectSwitchRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_object_switch_enabled = Operation(
        INFO,
        "set_object_switch_enabled",
        DcaBinding("PATCH", f"{ROOT}/objectSwitch/enabled", body="value", body_field="enabled"),
        params=SetObjectSwitchEnabledRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    set_object_switch_time = Operation(
        INFO,
        "set_object_switch_time",
        DcaBinding("PATCH", f"{ROOT}/objectSwitch/time", body="value", body_field="time"),
        params=SetObjectSwitchTimeRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_scenario_configuration = Operation(
        INFO,
        "get_scenario_configuration",
        DcaBinding("GET", f"{ROOT}/scenarioConfiguration"),
        result=ScenarioConfiguration,
        access="admin",
        effect="read",
    )
    set_scenario_configuration_scenarios = Operation(
        INFO,
        "set_scenario_configuration_scenarios",
        DcaBinding("PATCH", f"{ROOT}/scenarioConfiguration/scenarios", body="value", body_field="scenarios"),
        params=SetScenarioConfigurationScenariosRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class AutopilotApi(SyncApi):
    """Autopilot API (``autopilot-config``, v1)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> Autopilot:
        """The whole Autopilot tree, including calibration, object switch and scenario configuration.

        Access: admin.
        """
        return self._run(OPS.get_all, None, {}, request_options)

    def update_all(self, *, enabled: bool | MISSING = MISSING, request_options: RequestOptions | None = None) -> None:
        """Turn the Autopilot on or off. Changes only the fields given. Access: admin."""
        self._run(OPS.update_all, None, {"enabled": enabled}, request_options)

    def set_enabled(self, *, enabled: bool, request_options: RequestOptions | None = None) -> None:
        """Turn the Autopilot on or off. Changes only the fields given. Access: admin."""
        self._run(OPS.set_enabled, None, {"enabled": enabled}, request_options)

    def get_in_solo_mode(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether the Autopilot is in solo mode (no remote PTZ connected). Access: admin."""
        return self._run(OPS.get_in_solo_mode, None, {}, request_options)

    def get_state(self, *, request_options: RequestOptions | None = None) -> AutopilotState:
        """The current state of the Autopilot. Access: admin."""
        return self._run(OPS.get_state, None, {}, request_options)

    def get_calibration(self, *, request_options: RequestOptions | None = None) -> Calibration:
        """Calibration status and calibrated channels. Access: admin."""
        return self._run(OPS.get_calibration, None, {}, request_options)

    def get_calibration_status(self, *, request_options: RequestOptions | None = None) -> CalibrationStatus:
        """The current calibration status. Access: admin."""
        return self._run(OPS.get_calibration_status, None, {}, request_options)

    def get_channels_calibrated(self, *, request_options: RequestOptions | None = None) -> ChannelsCalibrated:
        """Which channels are calibrated to the remote PTZ. Access: admin."""
        return self._run(OPS.get_channels_calibrated, None, {}, request_options)

    def abort_calibration(self, *, request_options: RequestOptions | None = None) -> None:
        """Abort the running calibration process. Access: admin."""
        self._run(OPS.abort_calibration, None, {}, request_options)

    def start_calibration(self, *, request_options: RequestOptions | None = None) -> None:
        """Start the calibration process.

        Poll ``get_calibration_status`` for the outcome.

        Access: admin.
        """
        self._run(OPS.start_calibration, None, {}, request_options)

    def get_object_switch(self, *, request_options: RequestOptions | None = None) -> ObjectSwitch:
        """Get the object switch settings. Access: admin."""
        return self._run(OPS.get_object_switch, None, {}, request_options)

    def update_object_switch(
        self,
        *,
        enabled: bool | MISSING = MISSING,
        time: ObjectSwitchTime | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update the object switch settings (only the given fields change).

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.update_object_switch, None, {"enabled": enabled, "time": time}, request_options)

    def set_object_switch_enabled(self, *, enabled: bool, request_options: RequestOptions | None = None) -> None:
        """Turn object switching on or off. Changes only the fields given. Access: admin."""
        self._run(OPS.set_object_switch_enabled, None, {"enabled": enabled}, request_options)

    def set_object_switch_time(self, *, time: ObjectSwitchTime, request_options: RequestOptions | None = None) -> None:
        """Set how long an object is tracked before switching, in seconds.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_object_switch_time, None, {"time": time}, request_options)

    def get_scenario_configuration(self, *, request_options: RequestOptions | None = None) -> ScenarioConfiguration:
        """Get the scenario configuration. Access: admin."""
        return self._run(OPS.get_scenario_configuration, None, {}, request_options)

    @overload
    def set_scenario_configuration_scenarios(
        self, request: SetScenarioConfigurationScenariosRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    def set_scenario_configuration_scenarios(
        self, /, *, scenarios: ScenariosData, request_options: RequestOptions | None = None
    ) -> None: ...
    def set_scenario_configuration_scenarios(
        self,
        request: SetScenarioConfigurationScenariosRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Configure the scenarios to track. Changes only the fields given. Access: admin."""
        self._run(OPS.set_scenario_configuration_scenarios, request, kwargs, request_options)


class AsyncAutopilotApi(AsyncApi):
    """Autopilot API (``autopilot-config``, v1)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> Autopilot:
        """The whole Autopilot tree, including calibration, object switch and scenario configuration.

        Access: admin.
        """
        return await self._run(OPS.get_all, None, {}, request_options)

    async def update_all(
        self, *, enabled: bool | MISSING = MISSING, request_options: RequestOptions | None = None
    ) -> None:
        """Turn the Autopilot on or off. Changes only the fields given. Access: admin."""
        await self._run(OPS.update_all, None, {"enabled": enabled}, request_options)

    async def set_enabled(self, *, enabled: bool, request_options: RequestOptions | None = None) -> None:
        """Turn the Autopilot on or off. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_enabled, None, {"enabled": enabled}, request_options)

    async def get_in_solo_mode(self, *, request_options: RequestOptions | None = None) -> bool:
        """Whether the Autopilot is in solo mode (no remote PTZ connected). Access: admin."""
        return await self._run(OPS.get_in_solo_mode, None, {}, request_options)

    async def get_state(self, *, request_options: RequestOptions | None = None) -> AutopilotState:
        """The current state of the Autopilot. Access: admin."""
        return await self._run(OPS.get_state, None, {}, request_options)

    async def get_calibration(self, *, request_options: RequestOptions | None = None) -> Calibration:
        """Calibration status and calibrated channels. Access: admin."""
        return await self._run(OPS.get_calibration, None, {}, request_options)

    async def get_calibration_status(self, *, request_options: RequestOptions | None = None) -> CalibrationStatus:
        """The current calibration status. Access: admin."""
        return await self._run(OPS.get_calibration_status, None, {}, request_options)

    async def get_channels_calibrated(self, *, request_options: RequestOptions | None = None) -> ChannelsCalibrated:
        """Which channels are calibrated to the remote PTZ. Access: admin."""
        return await self._run(OPS.get_channels_calibrated, None, {}, request_options)

    async def abort_calibration(self, *, request_options: RequestOptions | None = None) -> None:
        """Abort the running calibration process. Access: admin."""
        await self._run(OPS.abort_calibration, None, {}, request_options)

    async def start_calibration(self, *, request_options: RequestOptions | None = None) -> None:
        """Start the calibration process.

        Poll ``get_calibration_status`` for the outcome.

        Access: admin.
        """
        await self._run(OPS.start_calibration, None, {}, request_options)

    async def get_object_switch(self, *, request_options: RequestOptions | None = None) -> ObjectSwitch:
        """Get the object switch settings. Access: admin."""
        return await self._run(OPS.get_object_switch, None, {}, request_options)

    async def update_object_switch(
        self,
        *,
        enabled: bool | MISSING = MISSING,
        time: ObjectSwitchTime | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update the object switch settings (only the given fields change).

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.update_object_switch, None, {"enabled": enabled, "time": time}, request_options)

    async def set_object_switch_enabled(self, *, enabled: bool, request_options: RequestOptions | None = None) -> None:
        """Turn object switching on or off. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_object_switch_enabled, None, {"enabled": enabled}, request_options)

    async def set_object_switch_time(
        self, *, time: ObjectSwitchTime, request_options: RequestOptions | None = None
    ) -> None:
        """Set how long an object is tracked before switching, in seconds.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_object_switch_time, None, {"time": time}, request_options)

    async def get_scenario_configuration(
        self, *, request_options: RequestOptions | None = None
    ) -> ScenarioConfiguration:
        """Get the scenario configuration. Access: admin."""
        return await self._run(OPS.get_scenario_configuration, None, {}, request_options)

    @overload
    async def set_scenario_configuration_scenarios(
        self, request: SetScenarioConfigurationScenariosRequest, /, *, request_options: RequestOptions | None = None
    ) -> None: ...
    @overload
    async def set_scenario_configuration_scenarios(
        self, /, *, scenarios: ScenariosData, request_options: RequestOptions | None = None
    ) -> None: ...
    async def set_scenario_configuration_scenarios(
        self,
        request: SetScenarioConfigurationScenariosRequest | None = None,
        /,
        *,
        request_options: RequestOptions | None = None,
        **kwargs: Any,
    ) -> None:
        """Configure the scenarios to track. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_scenario_configuration_scenarios, request, kwargs, request_options)
