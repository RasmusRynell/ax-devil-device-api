from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from ..core.endpoints import TransportEndpoint
from ..utils.errors import FeatureError
from .base import FeatureClient

CLASSIC_DISCOVERY_ENDPOINT = TransportEndpoint("POST", "/axis-cgi/apidiscovery.cgi")
CLASSIC_API_STATES = {"released", "alpha", "beta", "deprecated"}
DCA_API_STATES = {"released", "alpha", "beta"}


@dataclass(frozen=True)
class ClassicDiscoveredAPI:
    """API entry returned by the classic VAPIX API Discovery service."""

    id: str
    version: str
    status: str
    documentation_url: str | None = None
    name: str | None = None


@dataclass(frozen=True)
class ClassicAPIDiscoveryResult:
    """Result of the classic ``getApiList`` operation."""

    api_version: str
    apis: tuple[ClassicDiscoveredAPI, ...]
    context: str | None = None


class ClassicAPIDiscoveryClient(FeatureClient[ClassicAPIDiscoveryResult]):
    """Client for classic anonymous POST discovery."""

    def get_api_list(
        self,
        *,
        api_id: str | None = None,
        version: str | None = None,
        context: str | None = None,
        api_version: str = "1.0",
    ) -> ClassicAPIDiscoveryResult:
        """Get public VAPIX APIs; omitted filters mean no filtering."""
        request: dict[str, Any] = {"apiVersion": api_version, "method": "getApiList"}
        if context is not None:
            request["context"] = context
        params = {
            key: value
            for key, value in (("id", api_id), ("version", version))
            if value is not None
        }
        if params:
            request["params"] = params
        response = self._request_discovery(
            CLASSIC_DISCOVERY_ENDPOINT,
            headers={"Content-Type": "application/json"},
            json=request,
        )
        payload = self._parse_response(response, "getApiList")
        data = payload.get("data")
        if not isinstance(data, dict) or not isinstance(data.get("apiList"), list):
            raise FeatureError(
                "invalid_response", "Classic API discovery has no apiList"
            )
        entries = []
        for item in data["apiList"]:
            if not isinstance(item, dict) or not all(
                isinstance(item.get(key), str) for key in ("id", "version", "status")
            ):
                raise FeatureError(
                    "invalid_response", "Classic API discovery contains an invalid API"
                )
            if item["status"] not in CLASSIC_API_STATES:
                raise FeatureError(
                    "invalid_response",
                    f"Invalid classic API status: {item['status']}",
                )
            if any(
                item.get(key) is not None and not isinstance(item.get(key), str)
                for key in ("docLink", "name")
            ):
                raise FeatureError(
                    "invalid_response",
                    "Classic API discovery contains an invalid optional API field",
                )
            entries.append(
                ClassicDiscoveredAPI(
                    item["id"],
                    item["version"],
                    item["status"],
                    item.get("docLink"),
                    item.get("name"),
                )
            )
        context = payload.get("context")
        if context is not None and not isinstance(context, str):
            raise FeatureError(
                "invalid_response", "Classic API discovery context is not a string"
            )
        return ClassicAPIDiscoveryResult(payload["apiVersion"], tuple(entries), context)

    def get_supported_versions(self) -> tuple[str, ...]:
        """Get versions supported by the classic discovery service."""
        response = self._request_discovery(
            CLASSIC_DISCOVERY_ENDPOINT,
            headers={"Content-Type": "application/json"},
            json={"method": "getSupportedVersions"},
        )
        payload = self._parse_response(response, "getSupportedVersions")
        data = payload.get("data")
        versions = data.get("apiVersions") if isinstance(data, dict) else None
        if (
            not isinstance(versions, list)
            or not versions
            or not all(isinstance(version, str) for version in versions)
        ):
            raise FeatureError(
                "invalid_response", "Classic API discovery has no apiVersions"
            )
        return tuple(versions)

    def _request_discovery(self, endpoint: TransportEndpoint, **kwargs: Any) -> Any:
        """Use anonymous transport, with a documented legacy auth fallback."""
        response = self.request_no_auth(endpoint, **kwargs)
        if response.status_code == 401 and self._has_auth_challenge(response):
            return self.request_after_challenge(endpoint, response, **kwargs)
        return response

    @staticmethod
    def _has_auth_challenge(response: Any) -> bool:
        """Return whether a 401 response advertises Basic or Digest auth."""
        header = response.headers.get("WWW-Authenticate", "")
        if not isinstance(header, str):
            return False
        in_quotes = False
        escaped = False
        token_start = 0
        for index, character in enumerate(header + ","):
            if escaped:
                escaped = False
                continue
            if character == "\\" and in_quotes:
                escaped = True
                continue
            if character == '"':
                in_quotes = not in_quotes
                continue
            if in_quotes:
                continue
            if character == ",":
                token = header[token_start:index].strip().split(None, 1)[0:1]
                if token and token[0].lower() in {"basic", "digest"}:
                    return True
                token_start = index + 1
        return False

    @staticmethod
    def _parse_response(response: Any, expected_method: str) -> dict[str, Any]:
        if response.status_code != 200:
            raise FeatureError(
                "request_failed",
                f"Classic API discovery failed: HTTP {response.status_code}",
            )
        try:
            payload = response.json()
        except ValueError as error:
            raise FeatureError(
                "invalid_response", "Classic API discovery response is not valid JSON"
            ) from error
        if not isinstance(payload, dict):
            raise FeatureError(
                "invalid_response", "Classic API discovery response is not an object"
            )
        if "error" in payload:
            error = payload["error"]
            if not isinstance(error, dict):
                raise FeatureError(
                    "api_error", "Classic API discovery returned a malformed error"
                )
            raise FeatureError(
                "api_error",
                str(error.get("message", "Unknown API error")),
                details=error,
            )
        if payload.get("method") != expected_method or not isinstance(
            payload.get("apiVersion"), str
        ):
            raise FeatureError(
                "invalid_response",
                "Classic API discovery response has an invalid envelope",
            )
        return payload


@dataclass
class DiscoveredAPI:
    """Represents a single API.

    Attributes:
        name: Name of the API (e.g. 'analytics-mqtt')
        version: Version identifier (e.g. 'v1')
        state: API state (e.g. 'beta')
        version_string: Full version string (e.g. '1.0.0-beta.1')
    """

    name: str
    version: str
    state: str
    version_string: str

    _urls: dict[str, str | None]

    _documentation: str | None = None
    _documentation_html: str | None = None
    _model: dict | None = None
    _openapi: dict | None = None
    _rest_ui: str | None = None

    # Reference to client for making requests
    _client: DiscoveryClient | None = None

    @classmethod
    def from_discovery_data(cls, name: str, version: str, data: dict) -> DiscoveredAPI:
        """Create an API instance from discovery response data."""
        if not isinstance(data, dict):
            raise FeatureError(
                "invalid_response", "Device Configuration API entry is not an object"
            )
        state = data.get("state")
        version_string = data.get("version")
        if not isinstance(state, str) or not isinstance(version_string, str):
            raise FeatureError(
                "invalid_response",
                "Device Configuration API entry has invalid state or version",
            )
        if state not in DCA_API_STATES:
            raise FeatureError(
                "invalid_response", f"Invalid Device Configuration API state: {state}"
            )
        _validate_dca_version(state, version_string)
        urls: dict[str, str | None] = {}
        for resource_name in (
            "doc",
            "doc_html",
            "model",
            "rest_api",
            "rest_openapi",
            "rest_ui",
        ):
            resource = data.get(resource_name)
            if resource is not None and not isinstance(resource, str):
                raise FeatureError(
                    "invalid_response",
                    f"Device Configuration API resource {resource_name} is not a string",
                )
            urls[resource_name] = resource
        return cls(
            name=name,
            version=version,
            state=state,
            version_string=version_string,
            _urls=urls,
        )

    def _ensure_client(self) -> None:
        """Ensure we have a client instance for making requests."""
        if not self._client:
            raise RuntimeError("API instance not properly initialized with client")

    def get_documentation(self) -> str:
        """Get the API's markdown documentation.

        Makes a request only on first access, then caches the result.
        """
        if self._documentation is not None:
            return self._documentation

        self._ensure_client()

        doc_url = self._urls.get("doc")
        if not doc_url:
            raise FeatureError(
                "missing_documentation",
                f"No documentation URL available for {self.name} {self.version}",
            )

        response = self._client.request(
            TransportEndpoint("GET", doc_url), headers={"Accept": "text/markdown"}
        )

        if response.status_code != 200:
            raise FeatureError(
                "doc_fetch_failed",
                f"Failed to fetch documentation: HTTP {response.status_code}",
            )

        self._documentation = response.text
        return self._documentation

    def get_model(self) -> dict:
        """Get the API's JSON model.

        Makes a request only on first access, then caches the result.
        """
        if self._model is not None:
            return self._model

        self._ensure_client()

        model_url = self._urls.get("model")
        if not model_url:
            raise FeatureError(
                "missing_model",
                f"No model URL available for {self.name} {self.version}",
            )

        response = self._client.request(
            TransportEndpoint("GET", model_url), headers={"Accept": "application/json"}
        )

        if response.status_code != 200:
            raise FeatureError(
                "model_fetch_failed",
                f"Failed to fetch model: HTTP {response.status_code}",
            )

        try:
            model = response.json()
        except ValueError as error:
            raise FeatureError(
                "invalid_response", "API model is not valid JSON"
            ) from error
        if not isinstance(model, dict):
            raise FeatureError("invalid_response", "API model is not an object")
        self._model = model
        return self._model

    def get_documentation_html(self) -> str:
        """Get the API's HTML documentation.

        Makes a request only on first access, then caches the result.
        """
        if self._documentation_html is not None:
            return self._documentation_html

        self._ensure_client()

        doc_url = self._urls.get("doc_html")
        if not doc_url:
            raise FeatureError(
                "missing_documentation_html",
                f"No HTML documentation URL available for {self.name} {self.version}",
            )

        response = self._client.request(
            TransportEndpoint("GET", doc_url), headers={"Accept": "text/html"}
        )

        if response.status_code != 200:
            raise FeatureError(
                "doc_html_fetch_failed",
                f"Failed to fetch HTML documentation: HTTP {response.status_code}",
            )

        self._documentation_html = response.text
        return self._documentation_html

    def get_openapi_spec(self) -> dict:
        """Get the API's OpenAPI specification.

        Makes a request only on first access, then caches the result.
        """
        if self._openapi is not None:
            return self._openapi

        self._ensure_client()

        openapi_url = self._urls.get("rest_openapi")
        if not openapi_url:
            raise FeatureError(
                "missing_openapi",
                f"No OpenAPI spec URL available for {self.name} {self.version}",
            )

        response = self._client.request(
            TransportEndpoint("GET", openapi_url),
            headers={"Accept": "application/json"},
        )

        if response.status_code != 200:
            raise FeatureError(
                "openapi_fetch_failed",
                f"Failed to fetch OpenAPI spec: HTTP {response.status_code}",
            )

        try:
            openapi = response.json()
        except ValueError as error:
            raise FeatureError(
                "invalid_response", "OpenAPI specification is not valid JSON"
            ) from error
        if not isinstance(openapi, dict):
            raise FeatureError(
                "invalid_response", "OpenAPI specification is not an object"
            )
        self._openapi = openapi
        return self._openapi

    def get_rest_ui(self) -> str:
        """Fetch the discovered REST UI resource as HTML."""
        if self._rest_ui is not None:
            return self._rest_ui
        self._ensure_client()
        rest_ui_url = self._urls.get("rest_ui")
        if not rest_ui_url:
            raise FeatureError(
                "missing_rest_ui",
                f"No REST UI URL available for {self.name} {self.version}",
            )
        response = self._client.request(
            TransportEndpoint("GET", rest_ui_url), headers={"Accept": "text/html"}
        )
        if response.status_code != 200:
            raise FeatureError(
                "rest_ui_fetch_failed",
                f"Failed to fetch REST UI: HTTP {response.status_code}",
            )
        self._rest_ui = response.text
        return self._rest_ui

    @property
    def rest_api_url(self) -> str:
        """Get the base URL for REST API endpoints."""
        return self._urls.get("rest_api") or "No REST API available"

    @property
    def rest_ui_url(self) -> str:
        """Get the URL for the Swagger UI."""
        return self._urls.get("rest_ui") or "No REST UI available"


@dataclass
class DiscoveredAPICollection:
    """Collection of all available APIs and their endpoints.

    This is the root structure returned by the discovery endpoint.
    Provides easy access to APIs by name and version.

    Attributes:
        apis: Dictionary of APIs by name and version
        raw_data: Original response data for future parsing
    """

    apis: dict[str, dict[str, DiscoveredAPI]]
    raw_data: dict

    @classmethod
    def create_from_response(
        cls, data: dict, client: DiscoveryClient
    ) -> DiscoveredAPICollection:
        """Create APICollection from discovery response data."""
        apis = {}

        if not isinstance(data, dict):
            raise FeatureError(
                "invalid_response", "Device Configuration discovery is not an object"
            )
        if not isinstance(data.get("framework_version"), str):
            raise FeatureError(
                "invalid_response",
                "Device Configuration discovery has an invalid framework version",
            )
        api_mappings = data.get("apis")
        if not isinstance(api_mappings, dict):
            raise FeatureError(
                "invalid_response",
                "Device Configuration discovery APIs are not an object",
            )

        for api_name, versions in api_mappings.items():
            if not isinstance(api_name, str) or not isinstance(versions, dict):
                raise FeatureError(
                    "invalid_response",
                    "Device Configuration discovery has an invalid API mapping",
                )
            apis[api_name] = {}
            for version, api_data in versions.items():
                if not isinstance(version, str):
                    raise FeatureError(
                        "invalid_response",
                        "Device Configuration discovery has an invalid version mapping",
                    )
                api = DiscoveredAPI.from_discovery_data(api_name, version, api_data)
                api._client = client
                apis[api_name][version] = api

        return cls(apis=apis, raw_data=data)

    def get_api(self, name: str, version: str | None = None) -> DiscoveredAPI | None:
        """Get a specific API by name and optionally version.

        If version is not specified, returns the highest released SemVer.
        Raises FeatureError when the API has no released version.
        """
        if name not in self.apis:
            return None

        if version:
            return self.apis[name].get(version)

        versions = [api for api in self.apis[name].values() if api.state == "released"]
        if not versions:
            raise FeatureError(
                "no_released_version",
                f"API {name} has no released version; specify an explicit version",
            )
        return (
            max(versions, key=lambda api: _semantic_version(api.version_string))
            if versions
            else None
        )

    def get_all_apis(self) -> list[DiscoveredAPI]:
        """Get all APIs as a flat list."""
        return [api for versions in self.apis.values() for api in versions.values()]

    def get_apis_by_name(self, name: str) -> list[DiscoveredAPI]:
        """Get all versions of a specific API."""
        return list(self.apis.get(name, {}).values())


class DiscoveryClient(FeatureClient[DiscoveredAPICollection]):
    """Client for API discovery operations.

    Provides access to the device's API discovery endpoint and helps manage
    API documentation and resources.
    """

    DISCOVER_ENDPOINT = TransportEndpoint("GET", "/config/discover")

    def discover(self) -> DiscoveredAPICollection:
        """Get information about available APIs.

        Returns:
            DiscoveredAPICollection with discovered APIs
        """
        response = self.request(
            self.DISCOVER_ENDPOINT, headers={"Accept": "application/json"}
        )

        if response.status_code != 200:
            details = None
            try:
                payload = response.json()
            except ValueError:
                payload = None

            if isinstance(payload, dict):
                error = payload.get("error")
                if isinstance(error, dict):
                    error_code = error.get("code")
                    error_message = error.get("message")
                    if error_code is not None and error_message is not None:
                        raise FeatureError(
                            str(error_code),
                            str(error_message),
                            details=error,
                        )
                    details = error
                elif "error" in payload:
                    details = payload

            raise FeatureError(
                "discovery_failed",
                f"Discovery request failed: HTTP {response.status_code}",
                details=details,
            )

        try:
            payload = response.json()
        except ValueError as error:
            raise FeatureError(
                "invalid_response",
                "Device Configuration discovery response is not valid JSON",
            ) from error
        return DiscoveredAPICollection.create_from_response(payload, self)


def _semantic_version(version: str) -> tuple[int, int, int, int, int]:
    """Sort DCA semantic versions, with released versions above prereleases."""
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)(?:-(alpha|beta)\.(\d+))?", version)
    if not match:
        raise FeatureError(
            "invalid_response", f"Invalid Device Configuration API version: {version}"
        )
    major, minor, patch, state, prerelease = match.groups()
    return (
        int(major),
        int(minor),
        int(patch),
        {None: 2, "beta": 1, "alpha": 0}[state],
        int(prerelease or 0),
    )


def _validate_dca_version(state: str, version: str) -> None:
    """Validate a Device Configuration API state against its official version form."""
    if state == "released":
        pattern = r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)"
    elif state in {"alpha", "beta"}:
        pattern = rf"(?:0|[1-9]\d*)\.0\.0-{state}\.(?:0|[1-9]\d*)"
    else:
        raise FeatureError(
            "invalid_response", f"Invalid Device Configuration API state: {state}"
        )
    if not re.fullmatch(pattern, version):
        raise FeatureError(
            "invalid_response",
            f"Device Configuration API {state} version has invalid form: {version}",
        )
