"""Tests for system settings features."""

import pytest

from src.ax_devil_device_api.utils.errors import FeatureError


class TestUserManagement:
    """Test suite for user account management via pwdgrp.cgi."""

    @pytest.mark.integration
    def test_get_users(self, client):
        """Test listing user accounts and groups."""
        users = client.system_settings.get_users()
        assert isinstance(users, dict), "Response should be a dictionary"
        assert "admin" in users or "digusers" in users, (
            "Response should contain standard group keys"
        )

    @pytest.mark.integration
    def test_add_update_remove_user(self, client):
        """Test full user lifecycle: add, update, remove."""
        username = "testuser"

        # Add
        result = client.system_settings.add_user(
            user=username, pwd="TestPass123", grp="users", sgrp="viewer",
            comment="integration test user",
        )
        assert "Created" in result or "account" in result.lower()

        try:
            # Verify present
            users = client.system_settings.get_users()
            found = any(
                username in [u.strip() for u in v.split(",")]
                for v in users.values()
            )
            assert found, (
                f"User {username} should appear in user listing after add"
            )

            # Update password
            result = client.system_settings.update_user(username, pwd="NewPass456")
            assert "Modified" in result or "account" in result.lower()
        finally:
            # Always clean up — ignore cleanup errors to avoid masking test failures
            try:
                client.system_settings.remove_user(username)
            except Exception:
                pass

        # Verify gone
        users = client.system_settings.get_users()
        assert not any(
            username in [u.strip() for u in v.split(",")]
            for v in users.values()
        ), (
            f"User {username} should not appear in any group after remove"
        )


class TestFactoryDefault:
    """Test suite for factory default operations.

    These tests are destructive and skipped by default.
    """

    @pytest.mark.integration
    @pytest.mark.skip(reason="Destructive: resets device to factory defaults")
    def test_factory_default(self, client):
        """Test soft factory default."""
        result = client.system_settings.factory_default()
        assert isinstance(result, str)

    @pytest.mark.integration
    @pytest.mark.skip(reason="Destructive: hard resets device including IP")
    def test_hard_factory_default(self, client):
        """Test hard factory default."""
        result = client.system_settings.hard_factory_default()
        assert isinstance(result, str)


class TestFirmwareUpgrade:
    """Test suite for firmware upgrade."""

    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires a firmware file and restarts device")
    def test_firmware_upgrade(self, client, tmp_path):
        """Test firmware upgrade with a real firmware file."""
        # This would need a real firmware .bin to be meaningful
        pass

    def test_invalid_upgrade_type_raises(self):
        """Test that an invalid upgrade_type raises FeatureError."""
        from unittest.mock import MagicMock
        from src.ax_devil_device_api.features.system_settings import SystemSettingsClient

        client = SystemSettingsClient(MagicMock())
        with pytest.raises(FeatureError):
            client.firmware_upgrade("/dev/null", upgrade_type="invalid")


class TestLogs:
    """Test suite for log retrieval."""

    @pytest.mark.integration
    def test_get_system_log(self, client):
        """Test retrieving the system log."""
        log = client.system_settings.get_system_log()
        assert isinstance(log, str), "System log should be a string"
        assert len(log) > 0, "System log should not be empty"

    @pytest.mark.integration
    def test_get_system_log_with_filter(self, client):
        """Test retrieving the system log with a text filter."""
        log = client.system_settings.get_system_log(text_filter="error")
        assert isinstance(log, str), "Filtered system log should be a string"

    @pytest.mark.integration
    def test_get_access_log(self, client):
        """Test retrieving the access log."""
        log = client.system_settings.get_access_log()
        assert isinstance(log, str), "Access log should be a string"
        assert len(log) > 0, "Access log should not be empty"
