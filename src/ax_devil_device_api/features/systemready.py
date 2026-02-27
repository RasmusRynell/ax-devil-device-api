"""Systemready API client for checking device readiness.

The VAPIX Systemready API makes it possible to find out, without authentication,
if the Axis device is ready to handle external communication, configurations and
video streaming on either the first or a consecutive boot up.

API Discovery ID: systemready
AXIS OS: 9.50 and later
"""

from typing import Any, Dict, List

from .base import FeatureClient
from ..core.endpoints import TransportEndpoint
from ..utils.errors import FeatureError


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
    JSON_HEADERS = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    def _request_no_auth_json(self, payload: Dict[str, Any]) -> Any:
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

        if response.status_code != 200:
            raise FeatureError(
                "request_failed",
                f"Request failed: HTTP {response.status_code}",
            )

        json_response = response.json()

        if "error" in json_response:
            error = json_response["error"]
            raise FeatureError(
                "api_error",
                error.get("message", "Unknown API error"),
                details={"code": error.get("code")},
            )

        return json_response.get("data", {})

    def systemready(self, timeout: int = 20) -> Dict[str, Any]:
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
        return self._request_no_auth_json({
            "apiVersion": "1.1",
            "method": "systemready",
            "params": {
                "timeout": timeout,
            },
        })

    def get_supported_versions(self) -> List[str]:
        """Retrieve supported API versions from the device.

        Makes an unauthenticated request.

        Returns:
            List of supported API version strings (e.g. ["1.0", "1.4"]).

        Raises:
            FeatureError: If the request fails or returns an API error.
        """
        data = self._request_no_auth_json({
            "method": "getSupportedVersions",
        })
        return data.get("apiVersions", [])
