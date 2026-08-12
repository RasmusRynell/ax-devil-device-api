"""Tests for shared pytest configuration helpers."""

from tests.conftest import get_device_credentials


def test_complete_axis_family_wins_without_mixing_values():
    """The complete AXIS family has priority over the legacy family."""
    environment = {
        "AXIS_TARGET_ADDR": "axis-host",
        "AXIS_TARGET_USER": "axis-user",
        "AXIS_TARGET_PASS": "axis-pass",
        "AX_DEVIL_TARGET_ADDR": "legacy-host",
        "AX_DEVIL_TARGET_USER": "legacy-user",
        "AX_DEVIL_TARGET_PASS": "legacy-pass",
    }

    assert get_device_credentials(environment) == (
        "axis-host",
        "axis-user",
        "axis-pass",
    )


def test_complete_legacy_family_is_used_when_axis_family_is_partial():
    """A complete legacy family is used when AXIS variables are incomplete."""
    environment = {
        "AXIS_TARGET_ADDR": "axis-host",
        "AX_DEVIL_TARGET_ADDR": "legacy-host",
        "AX_DEVIL_TARGET_USER": "legacy-user",
        "AX_DEVIL_TARGET_PASS": "legacy-pass",
    }

    assert get_device_credentials(environment) == (
        "legacy-host",
        "legacy-user",
        "legacy-pass",
    )


def test_incomplete_credential_families_are_rejected():
    """Incomplete families do not produce mixed or partial credentials."""
    environment = {
        "AXIS_TARGET_ADDR": "axis-host",
        "AXIS_TARGET_USER": "axis-user",
        "AX_DEVIL_TARGET_ADDR": "legacy-host",
        "AX_DEVIL_TARGET_PASS": "legacy-pass",
    }

    assert get_device_credentials(environment) is None
