"""Base classes for generated API classes.

A generated method only names its operation and forwards its arguments:

    def get_client_status(self, *, request_options=None) -> ClientStatus:
        return self._run(OPS.get_client_status, None, {}, request_options)

Argument validation, protocol dispatch, retries and I/O all happen below.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from pydantic import MISSING

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, Model, Operation, flow_for

if TYPE_CHECKING:
    from ..device import AsyncDevice, Device


def build_params(op: Operation[Any], request: Model | None, kwargs: dict[str, Any]) -> Model | None:
    """Validate call arguments into the operation's params model.

    Either a ready request model or keyword arguments, not both. Keyword
    arguments left at ``MISSING`` are dropped, so they count as not set.
    """
    args = {k: v for k, v in kwargs.items() if v is not MISSING}
    if request is not None:
        if args:
            raise TypeError(f"{op.api.id}.{op.id}: pass either a request object or keyword arguments, not both")
        if op.params is None or not isinstance(request, op.params):
            expected = op.params.__name__ if op.params else "no request"
            raise TypeError(f"{op.api.id}.{op.id} expects {expected}, got {type(request).__name__}")
        return request
    if op.params is None:
        if args:
            raise TypeError(f"{op.api.id}.{op.id} takes no arguments, got: {', '.join(sorted(args))}")
        return None
    return op.params(**args)


class SyncApi:
    INFO: ClassVar[ApiInfo]

    def __init__(self, device: Device) -> None:
        self._device = device

    def _run(self, op: Operation[Any], request: Model | None, kwargs: dict[str, Any], options: RequestOptions | None) -> Any:
        params = build_params(op, request, kwargs)
        return self._device._execute(op, flow_for(op, params, self._device._state), options)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.INFO.id}>"


class AsyncApi:
    INFO: ClassVar[ApiInfo]

    def __init__(self, device: AsyncDevice) -> None:
        self._device = device

    async def _run(
        self, op: Operation[Any], request: Model | None, kwargs: dict[str, Any], options: RequestOptions | None
    ) -> Any:
        params = build_params(op, request, kwargs)
        return await self._device._execute(op, flow_for(op, params, self._device._state), options)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.INFO.id}>"
