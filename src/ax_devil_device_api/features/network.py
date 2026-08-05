import re
from typing import Any

from ..core.endpoints import TransportEndpoint
from ..utils.errors import FeatureError
from .base import FeatureClient


class NetworkClient(FeatureClient):
    """Client for network configuration operations."""

    # Endpoint definitions
    NETWORK_SETTINGS_ENDPOINT = TransportEndpoint(
        "POST", "/axis-cgi/network_settings.cgi"
    )

    def get_network_info(self) -> dict[str, Any]:
        """Get network interface information."""
        versions_response = self.request(
            self.NETWORK_SETTINGS_ENDPOINT, json={"method": "getSupportedVersions"}
        )
        version_data = self.parse_json_api_response(
            versions_response,
            "network settings version discovery",
            "getSupportedVersions",
        ).get("data")
        if not isinstance(version_data, dict):
            raise FeatureError(
                "invalid_response",
                "Network settings version response has no data object",
            )
        supported = version_data.get("supportedVersions")
        if (
            not isinstance(supported, list)
            or not supported
            or not all(isinstance(v, str) for v in supported)
        ):
            raise FeatureError(
                "unsupported_version",
                "Device returned no valid network settings API versions",
            )
        if not all(re.fullmatch(r"\d+\.\d+", version) for version in supported):
            raise FeatureError(
                "unsupported_version",
                "Device returned invalid network settings API versions",
            )
        version = max(
            supported, key=lambda value: tuple(int(part) for part in value.split("."))
        )
        response = self.request(
            self.NETWORK_SETTINGS_ENDPOINT,
            json={"apiVersion": version, "method": "getNetworkInfo"},
        )
        data = self.parse_json_api_response(
            response, "network info", "getNetworkInfo"
        ).get("data")
        if not isinstance(data, dict):
            raise FeatureError(
                "invalid_response", "Network info response has no data object"
            )
        return data
