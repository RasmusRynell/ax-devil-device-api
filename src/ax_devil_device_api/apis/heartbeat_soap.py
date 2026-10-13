# GENERATED from specs/apis/network-video/heartbeat-soap.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Send heartbeats to a device through the SOAP twin of the Heartbeat service (see heartbeat for the JSON form).

Docs: https://developer.axis.com/vapix/network-video/heartbeat-service-api/
"""

from __future__ import annotations

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Family, Model, Operation, ParamDiscovery, ServiceDiscovery
from .._protocols.soap import SoapBinding
from .._protocols.xmlmap import XmlField, XmlMap
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class HeartbeatSoapRequest(Model):
    duration: int = Field(validation_alias="axhbt:Duration", serialization_alias="axhbt:Duration")
    """Heartbeat duration, that is, the time before a heartbeat lost event is emitted. Unit: milliseconds."""


class HeartbeatSoapResult(Model):
    session_id: str = Field(validation_alias="axhbt:SessionId", serialization_alias="axhbt:SessionId")
    """Session identifier. It remains the same as long as the heartbeat is kept alive; a change between two successive calls means the heartbeat lost event has been emitted."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/vapix/services"

INFO = ApiInfo(
    id="heartbeat-soap",
    name="Heartbeat service API (SOAP)",
    family=Family.SOAP,
    discovery=(
        ParamDiscovery("Properties.API.Heartbeat.Heartbeat", "yes"),
        ParamDiscovery("Properties.API.Heartbeat.Version", "1.0", ">="),
        ServiceDiscovery("http://www.axis.com/vapix/ws/Heartbeat"),
    ),
    docs=("https://developer.axis.com/vapix/network-video/heartbeat-service-api/",),
)


class OPS:
    heartbeat_soap = Operation(
        INFO,
        "heartbeat_soap",
        SoapBinding(
            "http://www.axis.com/vapix/ws/Heartbeat/Heartbeat",
            "Heartbeat",
            "http://www.axis.com/vapix/ws/Heartbeat",
            reply=XmlMap(fields=(XmlField("axhbt:SessionId", source="child", name="SessionId"),)),
            namespaces=(("axhbt", "http://www.axis.com/vapix/ws/Heartbeat"),),
        ),
        params=HeartbeatSoapRequest,
        result=HeartbeatSoapResult,
        access="admin",
        effect="action",
    )


# ---------------------------------------------------------------------------
# API classes


class HeartbeatSoapApi(SyncApi):
    """Heartbeat service API (SOAP) (``heartbeat-soap``)."""

    INFO = INFO

    def heartbeat_soap(self, *, duration: int, request_options: RequestOptions | None = None) -> HeartbeatSoapResult:
        """Send a heartbeat via SOAP.

        Heartbeats should be sent at regular intervals, typically within a few seconds. To keep the
        heartbeat alive, send a new heartbeat before Duration expires. If a heartbeat expires, the session
        identifier in the response changes and the heartbeat lost event becomes true.

        Access: admin.
        """
        return self._run(OPS.heartbeat_soap, None, {"duration": duration}, request_options)


class AsyncHeartbeatSoapApi(AsyncApi):
    """Heartbeat service API (SOAP) (``heartbeat-soap``)."""

    INFO = INFO

    async def heartbeat_soap(
        self, *, duration: int, request_options: RequestOptions | None = None
    ) -> HeartbeatSoapResult:
        """Send a heartbeat via SOAP.

        Heartbeats should be sent at regular intervals, typically within a few seconds. To keep the
        heartbeat alive, send a new heartbeat before Duration expires. If a heartbeat expires, the session
        identifier in the response changes and the heartbeat lost event becomes true.

        Access: admin.
        """
        return await self._run(OPS.heartbeat_soap, None, {"duration": duration}, request_options)
