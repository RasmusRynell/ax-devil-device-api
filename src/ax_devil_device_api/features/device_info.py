import re
from typing import Any

from ..core.endpoints import TransportEndpoint
from ..utils.errors import FeatureError
from .base import FeatureClient


def get_device_info_from_params(params: dict[str, str]) -> dict[str, Any]:
    """Create device info dictionary from parameter dictionary.

    Args:
        params: Dictionary of device parameters

    Returns:
        Dictionary containing device information with fields:
        - model: Device model name (e.g., "AXIS Q1656")
        - product_type: Type of device (e.g., "Box Camera")
        - product_number: Short product number (e.g., "Q1656")
        - serial_number: Unique serial number
        - hardware_id: Hardware identifier
        - firmware_version: Current firmware version
        - build_date: Firmware build date
        - ptz_support: List of supported PTZ modes
        - analytics_support: Whether analytics are supported
    """

    def get_param(*keys: str, default: str = "unknown") -> str:
        for key in keys:
            if key in params:
                return params[key]
            if f"root.{key}" in params:
                return params[f"root.{key}"]
        return default

    ptz_modes = get_param("Properties.PTZ.DriverModeList", default="").split(",")
    ptz_support = [mode.strip() for mode in ptz_modes if mode.strip()]

    analytics_support = any(
        key
        for key in params
        if "analytics" in key.lower() or "objectdetection" in key.lower()
    )

    return {
        "model": get_param("ProdShortName", "Brand.ProdShortName"),
        "product_type": get_param("ProdType", "Brand.ProdType"),
        "product_number": get_param("ProdNbr", "Brand.ProdNbr"),
        "serial_number": get_param("SerialNumber", "Properties.System.SerialNumber"),
        "hardware_id": get_param("HardwareID", "Properties.System.HardwareID"),
        "firmware_version": get_param("Version", "Properties.Firmware.Version"),
        "build_date": get_param("BuildDate", "Properties.Firmware.BuildDate"),
        "ptz_support": ptz_support,
        "analytics_support": analytics_support,
        "metadata_support": get_param("Properties.API.Metadata.Metadata") == "yes",
        "Onvif Replay Extention": get_param("Properties.API.Onvif.ReplayExtension")
        == "yes",
    }


class DeviceInfoClient(FeatureClient):
    """Client for basic device operations."""

    BASIC_DEVICE_INFO_ENDPOINT = TransportEndpoint(
        "POST", "/axis-cgi/basicdeviceinfo.cgi"
    )
    FIRMWARE_MANAGEMENT_ENDPOINT = TransportEndpoint(
        "POST", "/axis-cgi/firmwaremanagement.cgi"
    )

    def get_info(self) -> dict[str, Any]:
        """Get basic device information."""
        return get_device_info_from_params(self.get_info_detailed())

    def get_info_detailed(self) -> dict[str, Any]:
        """Get detailed device information"""

        return self._get_basic_device_info("getAllProperties")

    def restart(self) -> bool:
        """Reboot through Firmware management; never retry this side effect."""
        version = self._get_supported_version(
            self.FIRMWARE_MANAGEMENT_ENDPOINT, "apiVersions"
        )
        response = self.request(
            self.FIRMWARE_MANAGEMENT_ENDPOINT,
            json={"apiVersion": version, "method": "reboot"},
        )
        try:
            payload = self.parse_json_api_response(response, "restart", "reboot")
        except FeatureError as error:
            if (
                error.code == "invalid_response"
                and "unexpected method" in error.message
            ):
                raise FeatureError(
                    "invalid_response",
                    "Restart response is not a valid reboot success envelope",
                ) from error
            raise
        if payload.get("data") != {}:
            raise FeatureError(
                "invalid_response",
                "Restart response is not a valid reboot success envelope",
            )
        return True

    def check_health(self) -> bool:
        """Return whether systemready reports the device as ready."""
        from .systemready import SystemReadyClient

        data = SystemReadyClient(self.device).systemready(timeout=20)
        if not isinstance(data, dict) or data.get("systemready") not in {"yes", "no"}:
            raise FeatureError(
                "invalid_response", "Systemready response has no valid readiness value"
            )
        return data["systemready"] == "yes"

    @staticmethod
    def _select_supported_version(versions: Any) -> str:
        """Select the highest advertised major/minor version."""
        if (
            not isinstance(versions, list)
            or not versions
            or not all(isinstance(v, str) for v in versions)
        ):
            raise FeatureError(
                "unsupported_version", "Device returned no valid supported API versions"
            )
        if not all(re.fullmatch(r"\d+\.\d+", version) for version in versions):
            raise FeatureError(
                "unsupported_version", "Device returned invalid supported API versions"
            )
        return max(
            versions, key=lambda value: tuple(int(part) for part in value.split("."))
        )

    def _get_supported_version(
        self, endpoint: TransportEndpoint, key: str, *, no_auth: bool = False
    ) -> str:
        """Bootstrap a JSON API and return its highest advertised version."""
        request_fn = self.request_no_auth if no_auth else self.request
        response = request_fn(endpoint, json={"method": "getSupportedVersions"})
        payload = self.parse_json_api_response(
            response, "version discovery", "getSupportedVersions"
        )
        data = payload.get("data")
        if not isinstance(data, dict):
            raise FeatureError(
                "invalid_response", "Version discovery response has no data object"
            )
        return self._select_supported_version(data.get(key))

    def _get_basic_device_info(
        self, method: str, *, authenticated: bool = True
    ) -> dict[str, Any]:
        """Fetch device info via basicdeviceinfo.cgi.

        Args:
            method: The VAPIX JSON-RPC method name
                (e.g. "getAllUnrestrictedProperties" or "getAllProperties").
            authenticated: If False the request bypasses the auth handler.
        """
        request_fn = self.request if authenticated else self.request_no_auth
        version_response = request_fn(
            self.BASIC_DEVICE_INFO_ENDPOINT, json={"method": "getSupportedVersions"}
        )
        version_data = self.parse_json_api_response(
            version_response,
            "basic device info version discovery",
            "getSupportedVersions",
        ).get("data")
        if not isinstance(version_data, dict):
            raise FeatureError(
                "invalid_response",
                "Basic device info version response has no data object",
            )
        api_version = self._select_supported_version(version_data.get("apiVersions"))
        response = request_fn(
            self.BASIC_DEVICE_INFO_ENDPOINT,
            json={"apiVersion": api_version, "method": method},
        )
        response_payload = self.parse_json_api_response(
            response, "basic device info", method
        )
        data = response_payload.get("data")
        if not isinstance(data, dict):
            raise FeatureError(
                "invalid_response", "Basic device info response has no data object"
            )
        data = data.get("propertyList")
        if not isinstance(data, dict) or not data:
            raise FeatureError(
                "invalid_response",
                "Basic device info response has no propertyList object",
            )
        return data

    def get_info_no_auth(self) -> dict[str, Any]:
        """Get device info without authentication using basicdeviceinfo.cgi."""
        return self._get_basic_device_info(
            "getAllUnrestrictedProperties", authenticated=False
        )

    def get_info_auth(self) -> dict[str, Any]:
        """Get device info with authentication using basicdeviceinfo.cgi."""
        return self._get_basic_device_info("getAllProperties")
