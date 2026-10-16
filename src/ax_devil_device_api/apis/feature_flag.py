# GENERATED from specs/apis/network-video/feature-flag.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Set, get and list device feature flags (toggle experimental features, gradual roll-outs).

Docs: https://developer.axis.com/vapix/network-video/feature-flag-service/
"""

from __future__ import annotations

from pydantic import Field

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

FlagValues = dict[str, bool]


class Flag(Model):
    """A feature flag with its metadata."""

    name: str
    """The name of the flag."""
    value: bool
    """The current flag value."""
    description: str
    """A short description of the flag."""
    default_value: bool = Field(validation_alias="defaultValue", serialization_alias="defaultValue")
    """The initial flag value."""


class SetFlagsRequest(Model):
    flag_values: FlagValues = Field(validation_alias="flagValues", serialization_alias="flagValues")
    """Flag name and value pairs. The flags are updated according to this map; other flags are unchanged."""


class SetFlagsResult(Model):
    result: str
    """``Success`` if the call was successful."""


class GetFlagsRequest(Model):
    names: list[str]
    """The names of the flags to retrieve."""


class GetFlagsResult(Model):
    flag_values: FlagValues = Field(validation_alias="flagValues", serialization_alias="flagValues")
    """The flag names and values, corresponding to the requested names."""


class ListFlagsResult(Model):
    flags: list[Flag]
    """All flags on the device with their metadata."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/featureflag.cgi"

INFO = ApiInfo(
    id="feature-flag",
    name="Feature Flag Service",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(ApiDiscovery("feature-flag"),),
    docs=("https://developer.axis.com/vapix/network-video/feature-flag-service/",),
    errors={
        1100: ErrorCode("Internal error.", "internal"),
        2100: ErrorCode("API version not supported.", "unsupported"),
        2101: ErrorCode("Invalid JSON.", "invalid_argument"),
        2102: ErrorCode("Method not supported.", "unsupported"),
        2103: ErrorCode("Required parameter missing.", "invalid_argument"),
        2104: ErrorCode("Invalid parameter value specified.", "invalid_argument"),
        2105: ErrorCode("Authorization failed.", "access_denied"),
        2106: ErrorCode("Authentication failed.", "access_denied"),
        2107: ErrorCode("Request too large.", "invalid_argument"),
        2200: ErrorCode("Flag does not exist; the message lists the unknown flags.", "not_found"),
    },
)


class OPS:
    set_flags = Operation(
        INFO,
        "set_flags",
        JsonRpcBinding("set", PATH),
        params=SetFlagsRequest,
        result=SetFlagsResult,
        access="admin",
        effect="write",
        write="patch",
    )
    get_flags = Operation(
        INFO,
        "get_flags",
        JsonRpcBinding("get", PATH),
        params=GetFlagsRequest,
        result=GetFlagsResult,
        access="admin",
        effect="read",
    )
    list_flags = Operation(
        INFO, "list_flags", JsonRpcBinding("listAll", PATH), result=ListFlagsResult, access="admin", effect="read"
    )


# ---------------------------------------------------------------------------
# API classes


class FeatureFlagApi(SyncApi):
    """Feature Flag Service (``feature-flag``, version 1)."""

    INFO = INFO

    def set_flags(self, *, flag_values: FlagValues, request_options: RequestOptions | None = None) -> SetFlagsResult:
        """Set the value of one or multiple flags. Changes only the fields given. Access: admin."""
        return self._run(OPS.set_flags, None, {"flag_values": flag_values}, request_options)

    def get_flags(self, *, names: list[str], request_options: RequestOptions | None = None) -> GetFlagsResult:
        """Retrieve the value of one or multiple flags. Access: admin."""
        return self._run(OPS.get_flags, None, {"names": names}, request_options)

    def list_flags(self, *, request_options: RequestOptions | None = None) -> ListFlagsResult:
        """Retrieve the value and metadata of all flags. Access: admin."""
        return self._run(OPS.list_flags, None, {}, request_options)


class AsyncFeatureFlagApi(AsyncApi):
    """Feature Flag Service (``feature-flag``, version 1)."""

    INFO = INFO

    async def set_flags(
        self, *, flag_values: FlagValues, request_options: RequestOptions | None = None
    ) -> SetFlagsResult:
        """Set the value of one or multiple flags. Changes only the fields given. Access: admin."""
        return await self._run(OPS.set_flags, None, {"flag_values": flag_values}, request_options)

    async def get_flags(self, *, names: list[str], request_options: RequestOptions | None = None) -> GetFlagsResult:
        """Retrieve the value of one or multiple flags. Access: admin."""
        return await self._run(OPS.get_flags, None, {"names": names}, request_options)

    async def list_flags(self, *, request_options: RequestOptions | None = None) -> ListFlagsResult:
        """Retrieve the value and metadata of all flags. Access: admin."""
        return await self._run(OPS.list_flags, None, {}, request_options)
