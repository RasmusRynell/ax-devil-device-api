"""Systemready API client for checking device readiness.

The VAPIX Systemready API makes it possible to find out, without authentication,
if the Axis device is ready to handle external communication, configurations and
video streaming on either the first or a consecutive boot up.

API Discovery ID: systemready
AXIS OS: 9.50 and later
"""

import re
from typing import Any, ClassVar

from ..core.endpoints import TransportEndpoint
from ..utils.errors import FeatureError
from .base import FeatureClient


class SystemReadyClient(FeatureClient):
    """Client for the Systemready API.

    Provides functionality for:
    - Checking if the device is ready for operation
    - Retrieving supported API versions

    Note: The systemready endpoint does not require authentication.

    Response data is returned as raw dicts so that new or changed fields
    from the device are passed through without code changes.
    """

    SYSTEMREADY_ENDPOINT = TransportEndpoint("POST", "/axis-cgi/systemready.cgi")
    JSON_HEADERS: ClassVar[dict[str, str]] = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    def _request_no_auth_json(
        self, payload: dict[str, Any], expected_method: str
    ) -> Any:
        """Send an unauthenticated JSON request and return the data payload.

        Handles HTTP status checks and API-level error responses so that
        individual methods stay concise.

        Returns:
            The ``data`` value from the JSON response.

        Raises:
            FeatureError: On HTTP or API-level errors.
        """
        response = self.request_no_auth(
            self.SYSTEMREADY_ENDPOINT,
            json=payload,
            headers=self.JSON_HEADERS,
        )

        json_response = self.parse_json_api_response(
            response, "Systemready", expected_method
        )
        data = json_response.get("data")
        if not isinstance(data, dict):
            raise FeatureError(
                "invalid_response", "Systemready response has no data object"
            )
        return data

    def systemready(self, timeout: int = 20) -> dict[str, Any]:
        """Check if the device is ready for operation.

        Makes an unauthenticated request to the systemready endpoint.
        The request will block up to the specified timeout waiting for
        the device to become ready.

        Args:
            timeout: Maximum time in seconds to wait for the device to respond.
                     Valid range is device-dependent; defaults to 20.

        Returns:
            Dict with device readiness data as returned by the API, e.g.::

                {
                    "systemready": "yes",
                    "needsetup": "no",
                    "uptime": "7800",
                    "bootid": "ebe1fa05-...",
                    "previewmode": "7200"   # only present when active
                }

        Raises:
            FeatureError: If the request fails or returns an API error.
        """
        versions = self.get_supported_versions()
        return self._request_no_auth_json(
            {
                "apiVersion": self._select_supported_version(versions),
                "method": "systemready",
                "params": {
                    "timeout": timeout,
                },
            },
            "systemready",
        )

    def get_supported_versions(self) -> list[str]:
        """Retrieve supported API versions from the device.

        Makes an unauthenticated request.

        Returns:
            List of supported API version strings (e.g. ["1.0", "1.4"]).

        Raises:
            FeatureError: If the request fails or returns an API error.
        """
        data = self._request_no_auth_json(
            {
                "method": "getSupportedVersions",
            },
            "getSupportedVersions",
        )
        versions = data.get("apiVersions")
        if (
            not isinstance(versions, list)
            or not versions
            or not all(isinstance(version, str) for version in versions)
        ):
            raise FeatureError(
                "invalid_response", "Systemready response has no valid API versions"
            )
        if not all(re.fullmatch(r"\d+\.\d+", version) for version in versions):
            raise FeatureError(
                "invalid_response", "Systemready response has malformed API versions"
            )
        return versions

    @staticmethod
    def _select_supported_version(versions: list[str]) -> str:
        """Select the highest supported major/minor API version."""
        return max(
            versions,
            key=lambda version: tuple(int(part) for part in version.split(".")),
        )
