# GENERATED from specs/apis/network-video/pencil-privacy-filter.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Add a black and white "pencil image" privacy effect to the video stream; select filter, configure flags, query capabilities.

Docs: https://developer.axis.com/vapix/network-video/pencil-privacy-filter/
"""

from __future__ import annotations

from typing import Any

from .._http.options import RequestOptions
from .._protocols.base import ApiDiscovery, ApiInfo, ApiVersion, ErrorCode, Family, Model, Operation
from .._protocols.jsonrpc import JsonRpcBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models


class FilterType(Model):
    """Selects a filter by type."""

    type: str
    """The filter type, for example ``pencil``."""


class FilterSetting(Model):
    type: str
    """The filter type, for example ``pencil``."""
    flags: dict[str, Any] | None = None
    """Flags of the filter. They differ by filter type, for example ``inverted`` (boolean) and ``threshold`` (integer). Use ``get_filter_capabilities`` to discover them."""


class SelectedFilter(Model):
    type: str
    """The current filter type; ``none`` if no filter is active."""


class FlagCapability(Model):
    type: str | None = None
    """Flag type, for example ``bool`` or ``integer``."""
    min: float | None = None
    max: float | None = None
    description: str | None = None


class FilterCapability(Model):
    type: str | None = None
    """The filter type."""
    description: str | None = None
    """Describes the filter type."""
    flags: list[dict[str, FlagCapability]] | None = None
    """Flags available for the filter. Each item is a single-key object from flag name to capability."""


class FilterCapabilities(Model):
    filters: list[FilterCapability] | None = None


class SetFilterSettingsRequest(Model):
    settings: list[FilterSetting]
    """One entry per filter type that receives new or updated flags."""


class GetFilterSettingsRequest(Model):
    filters: list[FilterType]
    """The filter types to check."""


class SetSelectedFilterRequest(Model):
    filters: list[FilterType]
    """The filter type that should be active."""


# ---------------------------------------------------------------------------
# Descriptors

PATH = "/axis-cgi/pencil.cgi"

INFO = ApiInfo(
    id="pencil-privacy-filter",
    name="Pencil privacy filter",
    family=Family.JSONRPC,
    major=1,
    known_versions=(ApiVersion(1, 0),),
    discovery=(ApiDiscovery("pencil-privacy-filter"),),
    docs=("https://developer.axis.com/vapix/network-video/pencil-privacy-filter/",),
    errors={
        1100: ErrorCode("Internal error", "internal"),
        2101: ErrorCode("Bad request. Invalid JSON", "invalid_argument"),
        2105: ErrorCode("Authorization failed", "access_denied"),
        2106: ErrorCode("Authentication failed", "access_denied"),
        2107: ErrorCode("Transport level error", "internal"),
    },
)


class OPS:
    set_filter_settings = Operation(
        INFO,
        "set_filter_settings",
        JsonRpcBinding("setFilterSettings", PATH, params_field="settings"),
        params=SetFilterSettingsRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_filter_settings = Operation(
        INFO,
        "get_filter_settings",
        JsonRpcBinding("getFilterSettings", PATH, params_field="filters"),
        params=GetFilterSettingsRequest,
        result=list[FilterSetting],
        access="admin",
        effect="read",
    )
    set_selected_filter = Operation(
        INFO,
        "set_selected_filter",
        JsonRpcBinding("setSelectedFilter", PATH, params_field="filters"),
        params=SetSelectedFilterRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_selected_filter = Operation(
        INFO,
        "get_selected_filter",
        JsonRpcBinding("getSelectedFilter", PATH),
        result=SelectedFilter,
        access="admin",
        effect="read",
    )
    get_filter_capabilities = Operation(
        INFO,
        "get_filter_capabilities",
        JsonRpcBinding("getFilterCapabilities", PATH),
        result=FilterCapabilities,
        access="admin",
        effect="read",
    )


# ---------------------------------------------------------------------------
# API classes


class PencilPrivacyFilterApi(SyncApi):
    """Pencil privacy filter (``pencil-privacy-filter``, version 1)."""

    INFO = INFO

    def set_filter_settings(
        self, settings: list[FilterSetting], *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the flag values of one or more filter types.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_filter_settings, None, {"settings": settings}, request_options)

    def get_filter_settings(
        self, filters: list[FilterType], *, request_options: RequestOptions | None = None
    ) -> list[FilterSetting]:
        """Get the current flag values of one or more filter types. Access: admin."""
        return self._run(OPS.get_filter_settings, None, {"filters": filters}, request_options)

    def set_selected_filter(self, filters: list[FilterType], *, request_options: RequestOptions | None = None) -> None:
        """Select which filter is active; ``none`` deactivates the filter.

        Changes only the fields given. Access: admin.
        """
        self._run(OPS.set_selected_filter, None, {"filters": filters}, request_options)

    def get_selected_filter(self, *, request_options: RequestOptions | None = None) -> SelectedFilter:
        """Get the currently active filter. Access: admin."""
        return self._run(OPS.get_selected_filter, None, {}, request_options)

    def get_filter_capabilities(self, *, request_options: RequestOptions | None = None) -> FilterCapabilities:
        """List all available filters with their supported flags. Access: admin."""
        return self._run(OPS.get_filter_capabilities, None, {}, request_options)


class AsyncPencilPrivacyFilterApi(AsyncApi):
    """Pencil privacy filter (``pencil-privacy-filter``, version 1)."""

    INFO = INFO

    async def set_filter_settings(
        self, settings: list[FilterSetting], *, request_options: RequestOptions | None = None
    ) -> None:
        """Set the flag values of one or more filter types.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_filter_settings, None, {"settings": settings}, request_options)

    async def get_filter_settings(
        self, filters: list[FilterType], *, request_options: RequestOptions | None = None
    ) -> list[FilterSetting]:
        """Get the current flag values of one or more filter types. Access: admin."""
        return await self._run(OPS.get_filter_settings, None, {"filters": filters}, request_options)

    async def set_selected_filter(
        self, filters: list[FilterType], *, request_options: RequestOptions | None = None
    ) -> None:
        """Select which filter is active; ``none`` deactivates the filter.

        Changes only the fields given. Access: admin.
        """
        await self._run(OPS.set_selected_filter, None, {"filters": filters}, request_options)

    async def get_selected_filter(self, *, request_options: RequestOptions | None = None) -> SelectedFilter:
        """Get the currently active filter. Access: admin."""
        return await self._run(OPS.get_selected_filter, None, {}, request_options)

    async def get_filter_capabilities(self, *, request_options: RequestOptions | None = None) -> FilterCapabilities:
        """List all available filters with their supported flags. Access: admin."""
        return await self._run(OPS.get_filter_capabilities, None, {}, request_options)
