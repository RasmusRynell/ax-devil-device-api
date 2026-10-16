# GENERATED from specs/apis/network-video/reposition-quadview.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Reorder the four dewarped sub views of a fisheye quad view, and enable/disable QuadEye (quad view plus a centre overview).

Docs: https://developer.axis.com/vapix/network-video/quadview-configuration/
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation, ParamDiscovery
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

SubViewOrder = list[Annotated[int, Field(ge=1, le=4)]]
QuadEyeValue = Literal["true", "false"]


class OrderResult(Model):
    id: SubViewOrder


class SetOrderRequest(Model):
    id: SubViewOrder
    """New order of the four sub views."""


class QuadEyeResult(Model):
    quadeye: QuadEyeValue


class SetQuadEyeValueRequest(Model):
    quadeye: bool
    """Whether QuadEye should be enabled."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/quadviewsetup.cgi"

INFO = ApiInfo(
    id="reposition-quadview",
    name="QuadView configuration",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(
        ApiDiscovery("reposition-quadview"),
        ParamDiscovery("Properties.QuadOverview.QuadViewOrder", "yes"),
        ParamDiscovery("Properties.QuadOverview.QuadOverview", "yes"),
    ),
    docs=("https://developer.axis.com/vapix/network-video/quadview-configuration/",),
    errors={
        1100: ErrorCode("Internal error", "internal"),
        2100: ErrorCode("API version not supported", "unsupported"),
        2101: ErrorCode("Invalid JSON", "invalid_argument"),
        2102: ErrorCode("Method not supported", "unsupported"),
        2103: ErrorCode("Required parameter missing", "invalid_argument"),
        2104: ErrorCode("Invalid parameter value specified", "invalid_argument"),
    },
)


class OPS:
    get_order = Operation(
        INFO, "get_order", JsonRpcBinding("getOrder", PATH), result=OrderResult, access="operator", effect="read"
    )
    set_order = Operation(
        INFO,
        "set_order",
        JsonRpcBinding("setOrder", PATH),
        params=SetOrderRequest,
        result=OrderResult,
        access="operator",
        effect="write",
        write="replace",
    )
    get_quad_eye_value = Operation(
        INFO,
        "get_quad_eye_value",
        JsonRpcBinding("getQuadEyeValue", PATH),
        result=QuadEyeResult,
        access="operator",
        effect="read",
    )
    set_quad_eye_value = Operation(
        INFO,
        "set_quad_eye_value",
        JsonRpcBinding("setQuadEyeValue", PATH),
        params=SetQuadEyeValueRequest,
        result=QuadEyeResult,
        access="operator",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class QuadViewConfigurationApi(SyncApi):
    """QuadView configuration (``reposition-quadview``, version 1)."""

    INFO = INFO

    def get_order(self, *, request_options: RequestOptions | None = None) -> OrderResult:
        """Get the order of the sub views in the quad view. Access: operator."""
        return self._run(OPS.get_order, None, {}, request_options)

    def set_order(self, id: SubViewOrder, *, request_options: RequestOptions | None = None) -> OrderResult:
        """Set the order of the sub views in the quad view.

        The device may override the order when the mounting parameter
        ``root.ImageSource.IO.CameraTiltOrientation`` is used. Returns the order now in effect.

        Replaces the whole configuration; fields left out return to their defaults. Access: operator.
        """
        return self._run(OPS.set_order, None, {"id": id}, request_options)

    def get_quad_eye_value(self, *, request_options: RequestOptions | None = None) -> QuadEyeResult:
        """Read whether QuadEye (quad view plus overview) is enabled. Access: operator."""
        return self._run(OPS.get_quad_eye_value, None, {}, request_options)

    def set_quad_eye_value(self, quadeye: bool, *, request_options: RequestOptions | None = None) -> QuadEyeResult:
        """Enable or disable QuadEye (quad view plus overview).

        Returns the value now in effect.

        Changes only the fields given. Access: operator.
        """
        return self._run(OPS.set_quad_eye_value, None, {"quadeye": quadeye}, request_options)


class AsyncQuadViewConfigurationApi(AsyncApi):
    """QuadView configuration (``reposition-quadview``, version 1)."""

    INFO = INFO

    async def get_order(self, *, request_options: RequestOptions | None = None) -> OrderResult:
        """Get the order of the sub views in the quad view. Access: operator."""
        return await self._run(OPS.get_order, None, {}, request_options)

    async def set_order(self, id: SubViewOrder, *, request_options: RequestOptions | None = None) -> OrderResult:
        """Set the order of the sub views in the quad view.

        The device may override the order when the mounting parameter
        ``root.ImageSource.IO.CameraTiltOrientation`` is used. Returns the order now in effect.

        Replaces the whole configuration; fields left out return to their defaults. Access: operator.
        """
        return await self._run(OPS.set_order, None, {"id": id}, request_options)

    async def get_quad_eye_value(self, *, request_options: RequestOptions | None = None) -> QuadEyeResult:
        """Read whether QuadEye (quad view plus overview) is enabled. Access: operator."""
        return await self._run(OPS.get_quad_eye_value, None, {}, request_options)

    async def set_quad_eye_value(
        self, quadeye: bool, *, request_options: RequestOptions | None = None
    ) -> QuadEyeResult:
        """Enable or disable QuadEye (quad view plus overview).

        Returns the value now in effect.

        Changes only the fields given. Access: operator.
        """
        return await self._run(OPS.set_quad_eye_value, None, {"quadeye": quadeye}, request_options)
