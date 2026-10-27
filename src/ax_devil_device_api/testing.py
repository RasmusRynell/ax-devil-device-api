"""Test helpers: a scriptable fake camera for unit-testing code that uses the library.

::

    camera = MockCamera()
    camera.identity(model="AXIS Q1656", firmware="11.9.0", serial="ACCC8E")
    camera.jsonrpc("/axis-cgi/mqtt/client.cgi", "getClientStatus",
                   data={"status": {"state": "active", "connectionStatus": "connected"}})
    with camera.device() as dev:
        assert dev.apis.mqtt_client.get_client_status().status.state == "active"
    assert camera.calls("getClientStatus")

Everything runs over one ``httpx.MockTransport``, so no network is used and
the same camera serves sync and async devices. Notes:

- Paths match exactly, as the device sees them. If you configure a
  ``base_path`` on the device, include it in the paths you register.
- A later registration for the same route (method, path, and for JSON-RPC the
  method name, and for ``cgi`` the ``match`` arguments) overrides earlier ones.
- Requests nothing matches get ``404`` and are still recorded.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qsl

import httpx

from ._http.config import Auth
from .device import AsyncDevice, Device

__all__ = ["MockCamera", "RecordedRequest"]

Handler = Callable[[httpx.Request], httpx.Response]

_BASIC_INFO = "/axis-cgi/basicdeviceinfo.cgi"
_API_DISCOVERY = "/axis-cgi/apidiscovery.cgi"
_GET_VERSIONS = "getSupportedVersions"


@dataclass(frozen=True)
class RecordedRequest:
    """One request the camera received (including failed and unmatched ones)."""

    method: str
    path: str
    query: dict[str, str]
    json: Any | None
    """Parsed JSON body, if the body was JSON."""
    form: dict[str, str] | None
    """Parsed form body, if the body was URL-encoded."""


@dataclass
class _Route:
    method: str | None
    path: str
    accepts: Callable[[RecordedRequest], bool]
    handler: Handler


@dataclass
class _Failure:
    path: str
    error: type[httpx.TransportError]
    remaining: int | None


def _record(request: httpx.Request) -> RecordedRequest:
    content_type = request.headers.get("content-type", "")
    body: Any | None = None
    form: dict[str, str] | None = None
    if request.content:
        if "json" in content_type:
            try:
                body = json.loads(request.content)
            except ValueError:
                body = None
        elif "x-www-form-urlencoded" in content_type:
            form = dict(parse_qsl(request.content.decode(), keep_blank_values=True))
    return RecordedRequest(request.method, request.url.path, dict(request.url.params.items()), body, form)


class MockCamera:
    """A fake Axis device. Register answers, then run your code against ``device()``."""

    def __init__(self) -> None:
        self.requests: list[RecordedRequest] = []
        self._routes: list[_Route] = []
        self._failures: list[_Failure] = []
        self._versioned: set[str] = set()

    # -- Registration -----------------------------------------------------

    def route(
        self,
        method: str,
        path: str,
        handler: Handler,
        *,
        accepts: Callable[[RecordedRequest], bool] | None = None,
    ) -> None:
        """Answer ``method path`` with a raw httpx handler (escape hatch)."""
        self._routes.append(_Route(method.upper(), path, accepts or (lambda _: True), handler))

    def jsonrpc(
        self,
        path: str,
        method: str,
        *,
        data: Any = None,
        error: tuple[int, str] | None = None,
        status: int = 200,
        versions: Sequence[str] | None = None,
    ) -> None:
        """Answer JSON-RPC ``method`` at ``path`` with ``data`` or an ``(code, message)`` error.

        ``getSupportedVersions`` for ``path`` is answered automatically
        (``("1.0",)`` unless ``versions`` is given).
        """
        if versions is not None or (path not in self._versioned and method != _GET_VERSIONS):
            self._register_versions(path, tuple(versions) if versions is not None else ("1.0",))
        if method == _GET_VERSIONS:
            self._versioned.add(path)
        self._jsonrpc(path, method, data, error, status)

    def _register_versions(self, path: str, versions: tuple[str, ...]) -> None:
        self._versioned.add(path)
        self._jsonrpc(path, _GET_VERSIONS, {"apiVersions": list(versions)}, None, 200)

    def _jsonrpc(self, path: str, method: str, data: Any, error: tuple[int, str] | None, status: int) -> None:
        body: dict[str, Any] = {"apiVersion": "1.0", "method": method}
        if error is not None:
            body["error"] = {"code": error[0], "message": error[1]}
        else:
            body["data"] = {} if data is None else data

        def accepts(recorded: RecordedRequest) -> bool:
            return isinstance(recorded.json, dict) and recorded.json.get("method") == method

        self.route("POST", path, lambda _: httpx.Response(status, json=body), accepts=accepts)

    def identity(self, *, model: str = "AXIS TEST", firmware: str = "11.0.0", serial: str = "000000000000", **properties: str) -> None:
        """Answer Basic device information (``getAllProperties``); extra keywords become properties."""
        props = {"ProdShortName": model, "Version": firmware, "SerialNumber": serial, **properties}
        self.jsonrpc(_BASIC_INFO, "getAllProperties", data={"propertyList": props})

    def api_list(self, apis: Mapping[str, str]) -> None:
        """Answer classic API discovery with ``{api id: version}``."""
        entries = [{"id": name, "version": version, "name": name, "status": "released"} for name, version in apis.items()]
        self._jsonrpc(_API_DISCOVERY, "getApiList", {"apiList": entries}, None, 200)

    def dca_apis(self, apis: Mapping[str, Sequence[str]]) -> None:
        """Answer ``GET /config/discover`` with ``{api name: [versions]}``."""
        body = {
            "framework_version": "1.0.0",
            "apis": {name: {v: {"state": "released", "version": "1.0.0"} for v in versions} for name, versions in apis.items()},
        }
        self.route("GET", "/config/discover", lambda _: httpx.Response(200, json=body))

    def rest(
        self,
        method: str,
        path: str,
        *,
        data: Any = None,
        error: tuple[int, str] | None = None,
        status: int | None = None,
    ) -> None:
        """Answer a Device Configuration call; ``status`` defaults to 200 (400 with ``error``)."""
        if error is not None:
            body: dict[str, Any] = {"status": "error", "error": {"code": error[0], "message": error[1]}}
            code = 400 if status is None else status
        else:
            body = {"status": "success"} if data is None else {"status": "success", "data": data}
            code = 200 if status is None else status
        self.route(method, path, lambda _: httpx.Response(code, json=body))

    def cgi(
        self,
        path: str,
        *,
        text: str | bytes = "",
        match: Mapping[str, str] | None = None,
        content_type: str = "text/plain",
        status: int = 200,
        method: str | None = None,
    ) -> None:
        """Answer a classic CGI with raw ``text``; ``match`` must be a subset of the query or form arguments."""
        wanted = dict(match or {})

        def accepts(recorded: RecordedRequest) -> bool:
            args = {**recorded.query, **(recorded.form or {})}
            return all(args.get(k) == v for k, v in wanted.items())

        content = text.encode() if isinstance(text, str) else text
        route = _Route(method.upper() if method else None, path, accepts,
                       lambda _: httpx.Response(status, content=content, headers={"content-type": content_type}))
        self._routes.append(route)

    def fail(self, path: str, error: type[httpx.TransportError], *, times: int | None = None) -> None:
        """Make requests to ``path`` raise ``error`` (all of them, or the next ``times``)."""
        self._failures.append(_Failure(path, error, times))

    # -- Inspection -------------------------------------------------------

    def calls(self, method: str) -> list[RecordedRequest]:
        """Recorded JSON-RPC requests whose ``method`` is ``method``."""
        return [r for r in self.requests if isinstance(r.json, dict) and r.json.get("method") == method]

    # -- Devices ----------------------------------------------------------

    def device(self, host: str = "camera.test", **kwargs: Any) -> Device:
        """A ``Device`` talking to this camera. Defaults to credentials ``("root", "pass")``; kwargs are forwarded."""
        credentials: Auth | tuple[str, str] | None = kwargs.pop("credentials", ("root", "pass"))
        return Device(host, credentials=credentials, transport=httpx.MockTransport(self._handle), **kwargs)

    def async_device(self, host: str = "camera.test", **kwargs: Any) -> AsyncDevice:
        """An ``AsyncDevice`` talking to this camera (see ``device``)."""
        credentials: Auth | tuple[str, str] | None = kwargs.pop("credentials", ("root", "pass"))
        return AsyncDevice(host, credentials=credentials, transport=httpx.MockTransport(self._handle), **kwargs)

    # -- Transport --------------------------------------------------------

    def _handle(self, request: httpx.Request) -> httpx.Response:
        recorded = _record(request)
        self.requests.append(recorded)
        for failure in self._failures:
            if failure.path == recorded.path and failure.remaining != 0:
                if failure.remaining is not None:
                    failure.remaining -= 1
                raise failure.error("mock failure", request=request)
        for route in reversed(self._routes):
            if route.path == recorded.path and route.method in (None, recorded.method) and route.accepts(recorded):
                return route.handler(request)
        return httpx.Response(404, text="no mock route")
