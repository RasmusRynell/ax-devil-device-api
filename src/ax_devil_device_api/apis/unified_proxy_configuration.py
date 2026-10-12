# GENERATED from specs/apis/device-configuration/unified-proxy-configuration-config.yaml. Do not edit.
# Regenerate with `uv run python -m codegen generate`.
"""Configure the device's global HTTP and HTTPS proxy and the list of hosts that bypass it.

Docs: https://developer.axis.com/vapix/device-configuration/proxy-configuration-api/
"""

from __future__ import annotations

from pydantic import MISSING, Field

from .._http.options import RequestOptions
from .._protocols.base import ApiInfo, DcaDiscovery, Family, Model, Operation
from .._protocols.dca import DcaBinding
from ._base import AsyncApi, SyncApi

# ---------------------------------------------------------------------------
# Models

NoProxy = list[str]
HttpProxy = str
HttpsProxy = str


class UnifiedProxyConfiguration(Model):
    """The whole API tree."""

    global_http_proxy: HttpProxy | None = Field(
        default=None, validation_alias="globalHttpProxy", serialization_alias="globalHttpProxy"
    )
    """Global HTTP proxy, for example `https://192.168.0.211:80`. An empty string means no proxy. The URL format is not documented."""
    global_https_proxy: HttpsProxy | None = Field(
        default=None, validation_alias="globalHttpsProxy", serialization_alias="globalHttpsProxy"
    )
    """Global HTTPS proxy. An empty string means no proxy."""
    global_no_proxy_list: NoProxy | None = Field(
        default=None, validation_alias="globalNoProxyList", serialization_alias="globalNoProxyList"
    )
    """Hosts and addresses that bypass the proxy."""


class UpdateAllRequest(Model):
    """Arguments of ``update_all``."""

    global_http_proxy: HttpProxy | None = Field(
        default=None, validation_alias="globalHttpProxy", serialization_alias="globalHttpProxy"
    )
    """Global HTTP proxy, for example `https://192.168.0.211:80`. An empty string means no proxy. The URL format is not documented."""
    global_https_proxy: HttpsProxy | None = Field(
        default=None, validation_alias="globalHttpsProxy", serialization_alias="globalHttpsProxy"
    )
    """Global HTTPS proxy. An empty string means no proxy."""
    global_no_proxy_list: NoProxy | None = Field(
        default=None, validation_alias="globalNoProxyList", serialization_alias="globalNoProxyList"
    )
    """Hosts and addresses that bypass the proxy."""


class SetGlobalHttpProxyRequest(Model):
    global_http_proxy: HttpProxy = Field(validation_alias="globalHttpProxy", serialization_alias="globalHttpProxy")
    """Global HTTP proxy, for example `https://192.168.0.211:80`. An empty string means no proxy. The URL format is not documented."""


class SetGlobalHttpsProxyRequest(Model):
    global_https_proxy: HttpsProxy = Field(validation_alias="globalHttpsProxy", serialization_alias="globalHttpsProxy")
    """Global HTTPS proxy. An empty string means no proxy."""


class SetGlobalNoProxyListRequest(Model):
    global_no_proxy_list: NoProxy = Field(validation_alias="globalNoProxyList", serialization_alias="globalNoProxyList")
    """Hosts and addresses that bypass the proxy."""


# ---------------------------------------------------------------------------
# Descriptors

ROOT = "/config/rest/unified-proxy-configuration/v1beta"

INFO = ApiInfo(
    id="unified-proxy-configuration-config",
    name="Proxy Configuration API",
    family=Family.DCA,
    discovery=(DcaDiscovery("unified-proxy-configuration", "v1beta"),),
    docs=("https://developer.axis.com/vapix/device-configuration/proxy-configuration-api/",),
)


class OPS:
    get_all = Operation(
        INFO, "get_all", DcaBinding("GET", ROOT), result=UnifiedProxyConfiguration, access="admin", effect="read"
    )
    update_all = Operation(
        INFO,
        "update_all",
        DcaBinding("PATCH", ROOT, body="object"),
        params=UpdateAllRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_global_http_proxy = Operation(
        INFO,
        "get_global_http_proxy",
        DcaBinding("GET", f"{ROOT}/globalHttpProxy"),
        result=HttpProxy,
        access="admin",
        effect="read",
    )
    set_global_http_proxy = Operation(
        INFO,
        "set_global_http_proxy",
        DcaBinding("PATCH", f"{ROOT}/globalHttpProxy", body="value", body_field="globalHttpProxy"),
        params=SetGlobalHttpProxyRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_global_https_proxy = Operation(
        INFO,
        "get_global_https_proxy",
        DcaBinding("GET", f"{ROOT}/globalHttpsProxy"),
        result=HttpsProxy,
        access="admin",
        effect="read",
    )
    set_global_https_proxy = Operation(
        INFO,
        "set_global_https_proxy",
        DcaBinding("PATCH", f"{ROOT}/globalHttpsProxy", body="value", body_field="globalHttpsProxy"),
        params=SetGlobalHttpsProxyRequest,
        access="admin",
        effect="write",
        write="patch",
    )
    get_global_no_proxy_list = Operation(
        INFO,
        "get_global_no_proxy_list",
        DcaBinding("GET", f"{ROOT}/globalNoProxyList"),
        result=NoProxy,
        access="admin",
        effect="read",
    )
    set_global_no_proxy_list = Operation(
        INFO,
        "set_global_no_proxy_list",
        DcaBinding("PATCH", f"{ROOT}/globalNoProxyList", body="value", body_field="globalNoProxyList"),
        params=SetGlobalNoProxyListRequest,
        access="admin",
        effect="write",
        write="patch",
    )


# ---------------------------------------------------------------------------
# API classes


class UnifiedProxyConfigurationApi(SyncApi):
    """Proxy Configuration API (``unified-proxy-configuration-config``, v1beta)."""

    INFO = INFO

    def get_all(self, *, request_options: RequestOptions | None = None) -> UnifiedProxyConfiguration:
        """All data of the Proxy Configuration API. Access: admin."""
        return self._run(OPS.get_all, None, {}, request_options)

    def update_all(
        self,
        *,
        global_http_proxy: HttpProxy | MISSING = MISSING,
        global_https_proxy: HttpsProxy | MISSING = MISSING,
        global_no_proxy_list: NoProxy | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update the Proxy Configuration API settings. Changes only the fields given. Access: admin."""
        self._run(
            OPS.update_all,
            None,
            {
                "global_http_proxy": global_http_proxy,
                "global_https_proxy": global_https_proxy,
                "global_no_proxy_list": global_no_proxy_list,
            },
            request_options,
        )

    def get_global_http_proxy(self, *, request_options: RequestOptions | None = None) -> HttpProxy:
        """Read the global HTTP proxy. Access: admin."""
        return self._run(OPS.get_global_http_proxy, None, {}, request_options)

    def set_global_http_proxy(
        self, *, global_http_proxy: HttpProxy, request_options: RequestOptions | None = None
    ) -> None:
        """Set the global http proxy of the device. Changes only the fields given. Access: admin."""
        self._run(OPS.set_global_http_proxy, None, {"global_http_proxy": global_http_proxy}, request_options)

    def get_global_https_proxy(self, *, request_options: RequestOptions | None = None) -> HttpsProxy:
        """Read the global HTTPS proxy. Access: admin."""
        return self._run(OPS.get_global_https_proxy, None, {}, request_options)

    def set_global_https_proxy(
        self, *, global_https_proxy: HttpsProxy, request_options: RequestOptions | None = None
    ) -> None:
        """Set the global https proxy of the device. Changes only the fields given. Access: admin."""
        self._run(OPS.set_global_https_proxy, None, {"global_https_proxy": global_https_proxy}, request_options)

    def get_global_no_proxy_list(self, *, request_options: RequestOptions | None = None) -> NoProxy:
        """Read the list of hosts that bypass the proxy. Access: admin."""
        return self._run(OPS.get_global_no_proxy_list, None, {}, request_options)

    def set_global_no_proxy_list(
        self, *, global_no_proxy_list: NoProxy, request_options: RequestOptions | None = None
    ) -> None:
        """Set the global no proxy list of the device. Changes only the fields given. Access: admin."""
        self._run(OPS.set_global_no_proxy_list, None, {"global_no_proxy_list": global_no_proxy_list}, request_options)


class AsyncUnifiedProxyConfigurationApi(AsyncApi):
    """Proxy Configuration API (``unified-proxy-configuration-config``, v1beta)."""

    INFO = INFO

    async def get_all(self, *, request_options: RequestOptions | None = None) -> UnifiedProxyConfiguration:
        """All data of the Proxy Configuration API. Access: admin."""
        return await self._run(OPS.get_all, None, {}, request_options)

    async def update_all(
        self,
        *,
        global_http_proxy: HttpProxy | MISSING = MISSING,
        global_https_proxy: HttpsProxy | MISSING = MISSING,
        global_no_proxy_list: NoProxy | MISSING = MISSING,
        request_options: RequestOptions | None = None,
    ) -> None:
        """Update the Proxy Configuration API settings. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.update_all,
            None,
            {
                "global_http_proxy": global_http_proxy,
                "global_https_proxy": global_https_proxy,
                "global_no_proxy_list": global_no_proxy_list,
            },
            request_options,
        )

    async def get_global_http_proxy(self, *, request_options: RequestOptions | None = None) -> HttpProxy:
        """Read the global HTTP proxy. Access: admin."""
        return await self._run(OPS.get_global_http_proxy, None, {}, request_options)

    async def set_global_http_proxy(
        self, *, global_http_proxy: HttpProxy, request_options: RequestOptions | None = None
    ) -> None:
        """Set the global http proxy of the device. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_global_http_proxy, None, {"global_http_proxy": global_http_proxy}, request_options)

    async def get_global_https_proxy(self, *, request_options: RequestOptions | None = None) -> HttpsProxy:
        """Read the global HTTPS proxy. Access: admin."""
        return await self._run(OPS.get_global_https_proxy, None, {}, request_options)

    async def set_global_https_proxy(
        self, *, global_https_proxy: HttpsProxy, request_options: RequestOptions | None = None
    ) -> None:
        """Set the global https proxy of the device. Changes only the fields given. Access: admin."""
        await self._run(OPS.set_global_https_proxy, None, {"global_https_proxy": global_https_proxy}, request_options)

    async def get_global_no_proxy_list(self, *, request_options: RequestOptions | None = None) -> NoProxy:
        """Read the list of hosts that bypass the proxy. Access: admin."""
        return await self._run(OPS.get_global_no_proxy_list, None, {}, request_options)

    async def set_global_no_proxy_list(
        self, *, global_no_proxy_list: NoProxy, request_options: RequestOptions | None = None
    ) -> None:
        """Set the global no proxy list of the device. Changes only the fields given. Access: admin."""
        await self._run(
            OPS.set_global_no_proxy_list, None, {"global_no_proxy_list": global_no_proxy_list}, request_options
        )
