"""Client for system settings operations (user management, factory default, logs, firmware)."""

import requests
from typing import Dict, Optional
from .base import FeatureClient
from ..core.endpoints import TransportEndpoint
from ..utils.errors import FeatureError


class SystemSettingsClient(FeatureClient):
    """Client for VAPIX system settings endpoints.

    Covers user account management (pwdgrp.cgi), factory default,
    firmware upgrade, and log retrieval.

    Note: restart.cgi lives in DeviceInfoClient; serverreport.cgi
    (zip_with_image) lives in DeviceDebugClient.
    """

    PWDGRP_GET_ENDPOINT = TransportEndpoint("GET", "/axis-cgi/pwdgrp.cgi")
    PWDGRP_POST_ENDPOINT = TransportEndpoint("POST", "/axis-cgi/pwdgrp.cgi")
    FACTORY_DEFAULT_ENDPOINT = TransportEndpoint("GET", "/axis-cgi/factorydefault.cgi")
    HARD_FACTORY_DEFAULT_ENDPOINT = TransportEndpoint("GET", "/axis-cgi/hardfactorydefault.cgi")
    FIRMWARE_UPGRADE_ENDPOINT = TransportEndpoint("POST", "/axis-cgi/firmwareupgrade.cgi")
    SYSTEM_LOG_ENDPOINT = TransportEndpoint("GET", "/axis-cgi/systemlog.cgi")
    ACCESS_LOG_ENDPOINT = TransportEndpoint("GET", "/axis-cgi/accesslog.cgi")

    # --- User management ---

    def get_users(self) -> Dict[str, str]:
        """List user accounts and group memberships.

        Returns:
            Dict mapping group names to comma-separated user lists,
            e.g. {"admin": "root,joe", "viewer": "root,joe,frank", ...}
        """
        response = self.request(
            self.PWDGRP_GET_ENDPOINT,
            params={"action": "get"},
        )
        if response.status_code != 200:
            raise FeatureError(
                "get_users_failed",
                f"Failed to get users: HTTP {response.status_code}",
            )
        return self._parse_pwdgrp_response(response)

    def add_user(
        self,
        user: str,
        pwd: str,
        grp: str = "users",
        sgrp: str = "viewer",
        comment: str = "",
        strict_pwd: bool = False,
    ) -> str:
        """Create a new user account.

        Args:
            user: Username (1-14 chars, a-z A-Z 0-9).
            pwd: Password for the account.
            grp: Primary group (typically "users").
            sgrp: Secondary groups defining role, e.g. "admin:operator:viewer:ptz".
            comment: Optional description.
            strict_pwd: Enforce VAPIX password standards.

        Returns:
            Response text from the device.
        """
        params: Dict[str, str] = {
            "action": "add",
            "user": user,
            "pwd": pwd,
            "grp": grp,
            "sgrp": sgrp,
            "comment": comment,
        }
        if strict_pwd:
            params["strict_pwd"] = "1"
        response = self.request(
            self.PWDGRP_POST_ENDPOINT, data=params,
            headers={"Content-Type": None},
        )
        if response.status_code != 200:
            raise FeatureError(
                "add_user_failed",
                f"Failed to add user: HTTP {response.status_code}",
            )
        text = response.text.strip()
        if "Error" in text:
            raise FeatureError("add_user_failed", text)
        return text

    def update_user(
        self,
        user: str,
        pwd: Optional[str] = None,
        sgrp: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> str:
        """Update an existing user account.

        Args:
            user: Username to update.
            pwd: New password.
            sgrp: New secondary groups / role.
            comment: New description.

        Returns:
            Response text from the device.
        """
        params: Dict[str, str] = {"action": "update", "user": user}
        if pwd is not None:
            params["pwd"] = pwd
        if sgrp is not None:
            params["sgrp"] = sgrp
        if comment is not None:
            params["comment"] = comment
        response = self.request(
            self.PWDGRP_POST_ENDPOINT, data=params,
            headers={"Content-Type": None},
        )
        if response.status_code != 200:
            raise FeatureError(
                "update_user_failed",
                f"Failed to update user: HTTP {response.status_code}",
            )
        text = response.text.strip()
        if "Error" in text:
            raise FeatureError("update_user_failed", text)
        return text

    def remove_user(self, user: str) -> str:
        """Remove a user account.

        Args:
            user: Username to remove.

        Returns:
            Response text from the device.
        """
        response = self.request(
            self.PWDGRP_POST_ENDPOINT,
            data={"action": "remove", "user": user},
            headers={"Content-Type": None},
        )
        if response.status_code != 200:
            raise FeatureError(
                "remove_user_failed",
                f"Failed to remove user: HTTP {response.status_code}",
            )
        text = response.text.strip()
        if "Error" in text:
            raise FeatureError("remove_user_failed", text)
        return text

    # --- Factory default ---

    def factory_default(self) -> str:
        """Soft factory default (preserves network settings).

        The device will restart automatically after reset.
        """
        response = self.request(self.FACTORY_DEFAULT_ENDPOINT)
        if response.status_code != 200:
            raise FeatureError(
                "factory_default_failed",
                f"Factory default failed: HTTP {response.status_code}",
            )
        return response.text.strip()

    def hard_factory_default(self) -> str:
        """Hard factory default (resets everything including IP).

        The device will restart automatically after reset.
        """
        response = self.request(self.HARD_FACTORY_DEFAULT_ENDPOINT)
        if response.status_code != 200:
            raise FeatureError(
                "hard_factory_default_failed",
                f"Hard factory default failed: HTTP {response.status_code}",
            )
        return response.text.strip()

    # --- Firmware upgrade ---

    _VALID_UPGRADE_TYPES = ("normal", "factorydefault")

    def firmware_upgrade(self, firmware_path: str, upgrade_type: str = "normal") -> str:
        """Upload and install a firmware file.

        The device will restart automatically after upgrade.

        Args:
            firmware_path: Local path to the .bin firmware file.
            upgrade_type: "normal" (keep settings) or "factorydefault".

        Returns:
            Response text from the device.
        """
        if upgrade_type not in self._VALID_UPGRADE_TYPES:
            raise FeatureError(
                "invalid_parameter",
                f"Invalid upgrade_type {upgrade_type!r}, must be one of {self._VALID_UPGRADE_TYPES}",
            )
        with open(firmware_path, "rb") as f:
            response = self.request(
                self.FIRMWARE_UPGRADE_ENDPOINT,
                params={"type": upgrade_type},
                files={"file": f},
                headers={"Content-Type": None},
            )
        if response.status_code != 200:
            raise FeatureError(
                "firmware_upgrade_failed",
                f"Firmware upgrade failed: HTTP {response.status_code}",
            )
        return response.text.strip()

    # --- Logs ---

    def get_system_log(self, text_filter: Optional[str] = None) -> str:
        """Get system log contents.

        Args:
            text_filter: Optional text to filter log entries on
                (available on AXIS OS 11.11.45+).

        Returns:
            System log as plain text.
        """
        params: Dict[str, str] = {}
        if text_filter:
            params["text"] = text_filter
        response = self.request(self.SYSTEM_LOG_ENDPOINT, params=params)
        if response.status_code != 200:
            raise FeatureError(
                "system_log_failed",
                f"Failed to get system log: HTTP {response.status_code}",
            )
        return response.text

    def get_access_log(self) -> str:
        """Get access log contents.

        Returns:
            Access log as plain text.
        """
        response = self.request(self.ACCESS_LOG_ENDPOINT)
        if response.status_code != 200:
            raise FeatureError(
                "access_log_failed",
                f"Failed to get access log: HTTP {response.status_code}",
            )
        return response.text

    # --- Helpers ---

    def _parse_pwdgrp_response(self, response: requests.Response) -> Dict[str, str]:
        """Parse pwdgrp.cgi 'get' response into a dict of group -> users."""
        result: Dict[str, str] = {}
        for line in response.text.strip().split("\n"):
            if "=" in line:
                key, value = line.split("=", 1)
                result[key.strip()] = value.strip().strip('"')
        return result
