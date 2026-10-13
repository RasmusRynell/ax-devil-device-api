# GENERATED from specs/apis/network-video/trigger-data.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""(Deprecated) Configure the Axis trigger data embedded in JPEG comment headers, MPEG-4 GOV headers and H.264 SEI messages, with param.cgi.

Docs: https://developer.axis.com/vapix/network-video/trigger-data/
"""

from __future__ import annotations

from collections.abc import Mapping

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ParamDiscovery
from .._protocols.cgi import CgiArg, CgiBinding, TextKv, TextOk
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class GetTriggerDataSettingsRequest(Model):
    group: str
    """The group to list, for example ``Image.I0.TriggerData``."""


class SetTriggerDataRequest(Model):
    parameters: dict[str, str]


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/param.cgi"

INFO = ApiInfo(
    id="trigger-data",
    name="Trigger data",
    family=Family.CGI,
    discovery=(ParamDiscovery("Properties.API.HTTP.Version", "3"),),
    status="deprecated",
    requires_firmware="5.00",
    docs=("https://developer.axis.com/vapix/network-video/trigger-data/",),
)


class OPS:
    get_trigger_data_settings = Operation(
        INFO,
        "get_trigger_data_settings",
        CgiBinding(
            PATH,
            fixed_query=(("action", "list"),),
            args=(CgiArg("group"),),
            reply=TextKv(strip_prefix="root."),
            accept="text/plain",
        ),
        params=GetTriggerDataSettingsRequest,
        result=dict[str, str],
        access="viewer",
        effect="read",
    )
    set_trigger_data = Operation(
        INFO,
        "set_trigger_data",
        CgiBinding(
            PATH, fixed_query=(("action", "update"),), args=(CgiArg("parameters", style="spread"),), reply=TextOk()
        ),
        params=SetTriggerDataRequest,
        access="operator",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class TriggerDataApi(SyncApi):
    """Trigger data (``trigger-data``)."""

    INFO = INFO

    def get_trigger_data_settings(self, group: str, *, request_options: RequestOptions | None = None) -> dict[str, str]:
        """Read trigger data parameters of a group as ``{"Image.I0.TriggerData.IOEnabled": "yes"}``.

        ``group`` is ``Image`` (``TriggerDataEnabled``), ``Image.I#.MPEG`` (``UserDataEnabled``,
        ``ConfigHeaderInterval``, ``UserDataInterval``) or ``Image.I#.TriggerData`` (``AudioEnabled``,
        ``IOEnabled``, ``MotionDetectionEnabled``, ``MotionLevelEnabled``, ``TamperingEnabled``,
        ``VideoLossEnabled``, ``UserTriggers``), where ``#`` is the image configuration, from 0 up to
        ``Image.NbrOfConfigs`` minus 1.

        Access: viewer.
        """
        return self._run(OPS.get_trigger_data_settings, None, {"group": group}, request_options)

    def set_trigger_data(self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None) -> None:
        """Enable trigger data and select the triggers, e.g. ``{"Image.TriggerDataEnabled": "yes"}``.

        ``parameters`` holds the parameters by full name: ``Image.TriggerDataEnabled`` (include trigger data
        in the video stream, default ``no``), ``Image.I#.MPEG.UserDataEnabled`` (needed to get trigger data
        in H.264 and MPEG-4), ``Image.I#.MPEG.ConfigHeaderInterval``, ``Image.I#.MPEG.UserDataInterval`` and
        the ``Image.I#.TriggerData`` parameters ``AudioEnabled``, ``IOEnabled``, ``MotionDetectionEnabled``,
        ``MotionLevelEnabled``, ``TamperingEnabled``, ``VideoLossEnabled`` and ``UserTriggers``. Values are
        ``yes`` or ``no``, an integer for the intervals, and ``<trigger1>;<trigger2>;...`` for
        ``UserTriggers``. Only the given parameters change, and the product must be restarted for them to
        take effect.

        Changes only the fields given. Access: operator.
        """
        self._run(OPS.set_trigger_data, None, {"parameters": dict(parameters)}, request_options)


class AsyncTriggerDataApi(AsyncApi):
    """Trigger data (``trigger-data``)."""

    INFO = INFO

    async def get_trigger_data_settings(
        self, group: str, *, request_options: RequestOptions | None = None
    ) -> dict[str, str]:
        """Read trigger data parameters of a group as ``{"Image.I0.TriggerData.IOEnabled": "yes"}``.

        ``group`` is ``Image`` (``TriggerDataEnabled``), ``Image.I#.MPEG`` (``UserDataEnabled``,
        ``ConfigHeaderInterval``, ``UserDataInterval``) or ``Image.I#.TriggerData`` (``AudioEnabled``,
        ``IOEnabled``, ``MotionDetectionEnabled``, ``MotionLevelEnabled``, ``TamperingEnabled``,
        ``VideoLossEnabled``, ``UserTriggers``), where ``#`` is the image configuration, from 0 up to
        ``Image.NbrOfConfigs`` minus 1.

        Access: viewer.
        """
        return await self._run(OPS.get_trigger_data_settings, None, {"group": group}, request_options)

    async def set_trigger_data(
        self, parameters: Mapping[str, str], *, request_options: RequestOptions | None = None
    ) -> None:
        """Enable trigger data and select the triggers, e.g. ``{"Image.TriggerDataEnabled": "yes"}``.

        ``parameters`` holds the parameters by full name: ``Image.TriggerDataEnabled`` (include trigger data
        in the video stream, default ``no``), ``Image.I#.MPEG.UserDataEnabled`` (needed to get trigger data
        in H.264 and MPEG-4), ``Image.I#.MPEG.ConfigHeaderInterval``, ``Image.I#.MPEG.UserDataInterval`` and
        the ``Image.I#.TriggerData`` parameters ``AudioEnabled``, ``IOEnabled``, ``MotionDetectionEnabled``,
        ``MotionLevelEnabled``, ``TamperingEnabled``, ``VideoLossEnabled`` and ``UserTriggers``. Values are
        ``yes`` or ``no``, an integer for the intervals, and ``<trigger1>;<trigger2>;...`` for
        ``UserTriggers``. Only the given parameters change, and the product must be restarted for them to
        take effect.

        Changes only the fields given. Access: operator.
        """
        await self._run(OPS.set_trigger_data, None, {"parameters": dict(parameters)}, request_options)
