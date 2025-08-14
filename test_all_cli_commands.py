#!/usr/bin/env python3
"""Comprehensive CLI test file to verify all commands can be imported and executed.

This test file validates that all unified CLI commands can be invoked without Python errors.
Tests the new unified CLI structure only (legacy commands have been removed in v1.0).
"""

import sys
import subprocess
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CommandTest:
    """Represents a CLI command test case."""
    name: str
    command: List[str]
    expected_in_help: Optional[str] = None
    should_fail_without_device: bool = True


class CLITester:
    """Tests CLI commands for import and help functionality."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def test_command_help(self, test: CommandTest) -> bool:
        """Test that a command's help can be displayed without errors."""
        try:
            # Test help command
            help_cmd = test.command + ['--help']
            result = subprocess.run(
                help_cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                self.errors.append(f"❌ {test.name}: Help command failed with code {result.returncode}")
                self.errors.append(f"   STDERR: {result.stderr}")
                return False
            
            # Check if expected text is in help output
            if test.expected_in_help and test.expected_in_help not in result.stdout:
                self.errors.append(f"❌ {test.name}: Expected text '{test.expected_in_help}' not found in help")
                return False
            
            print(f"✅ {test.name}: Help command works")
            return True
            
        except subprocess.TimeoutExpired:
            self.errors.append(f"❌ {test.name}: Help command timed out")
            return False
        except Exception as e:
            self.errors.append(f"❌ {test.name}: Exception during help test: {e}")
            return False
    
    def test_command_import(self, module_path: str, test_name: str) -> bool:
        """Test that a CLI module can be imported without errors."""
        try:
            # Test import via subprocess to avoid polluting current namespace
            import_cmd = [
                sys.executable, '-c', 
                f'import {module_path}; print("Import successful")'
            ]
            result = subprocess.run(
                import_cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                self.errors.append(f"❌ {test_name}: Import failed")
                self.errors.append(f"   STDERR: {result.stderr}")
                return False
            
            print(f"✅ {test_name}: Module imports successfully")
            return True
            
        except Exception as e:
            self.errors.append(f"❌ {test_name}: Exception during import test: {e}")
            return False
    
    def run_test(self, test: CommandTest) -> None:
        """Run a single command test."""
        if self.test_command_help(test):
            self.passed += 1
        else:
            self.failed += 1
    
    def run_import_test(self, module_path: str, test_name: str) -> None:
        """Run a single import test."""
        if self.test_command_import(module_path, test_name):
            self.passed += 1
        else:
            self.failed += 1
    
    def print_summary(self) -> None:
        """Print test summary."""
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success rate: {(self.passed/total*100):.1f}%" if total > 0 else "0%")
        
        if self.errors:
            print(f"\n{'='*60}")
            print(f"ERRORS")
            print(f"{'='*60}")
            for error in self.errors:
                print(error)
        
        if self.failed > 0:
            sys.exit(1)


def main():
    """Run all CLI tests."""
    print("🧪 Starting comprehensive CLI test suite")
    print("=" * 60)
    
    tester = CLITester()
    
    # Test main unified CLI
    unified_cli_tests = [
        CommandTest(
            "Main CLI Help",
            ["ax-devil-device-api"],
            expected_in_help="Unified CLI for Axis device APIs"
        ),
        CommandTest(
            "Main CLI Version",
            ["ax-devil-device-api", "--version"],
            expected_in_help="ax-devil-device-api, version"
        ),
        CommandTest(
            "Device Subcommand Help", 
            ["ax-devil-device-api", "device"],
            expected_in_help="Manage device operations"
        ),
        CommandTest(
            "Device Info Help",
            ["ax-devil-device-api", "device", "info"],
            expected_in_help="Get device information"
        ),
        CommandTest(
            "Device Health Help",
            ["ax-devil-device-api", "device", "health"],
            expected_in_help="Check if the device is responsive"
        ),
        CommandTest(
            "Device Restart Help",
            ["ax-devil-device-api", "device", "restart"],
            expected_in_help="Restart the device"
        ),
        CommandTest(
            "Network Subcommand Help",
            ["ax-devil-device-api", "network"],
            expected_in_help="Manage network operations"
        ),
        CommandTest(
            "Network Info Help",
            ["ax-devil-device-api", "network", "info"],
            expected_in_help="Get network interface information"
        ),
        CommandTest(
            "Media Subcommand Help",
            ["ax-devil-device-api", "media"],
            expected_in_help="Manage media operations"
        ),
        CommandTest(
            "Media Snapshot Help",
            ["ax-devil-device-api", "media", "snapshot"],
            expected_in_help="Capture JPEG snapshot"
        ),
        CommandTest(
            "MQTT Subcommand Help",
            ["ax-devil-device-api", "mqtt"],
            expected_in_help="Manage MQTT client settings"
        ),
        CommandTest(
            "MQTT Activate Help",
            ["ax-devil-device-api", "mqtt", "activate"],
            expected_in_help="Activate MQTT client"
        ),
        CommandTest(
            "MQTT Configure Help",
            ["ax-devil-device-api", "mqtt", "configure"],
            expected_in_help="Configure MQTT broker settings"
        ),
        CommandTest(
            "SSH Subcommand Help",
            ["ax-devil-device-api", "ssh"],
            expected_in_help="Manage SSH users"
        ),
        CommandTest(
            "SSH List Help",
            ["ax-devil-device-api", "ssh", "list"],
            expected_in_help="List all SSH users"
        ),
        CommandTest(
            "SSH Add Help", 
            ["ax-devil-device-api", "ssh", "add"],
            expected_in_help="Add a new SSH user"
        ),
        CommandTest(
            "Geocoordinates Subcommand Help",
            ["ax-devil-device-api", "geocoordinates"],
            expected_in_help="Manage geographic coordinates"
        ),
        CommandTest(
            "Geocoordinates Location Help",
            ["ax-devil-device-api", "geocoordinates", "location"],
            expected_in_help="Get or set device location coordinates"
        ),
        CommandTest(
            "Geocoordinates Location Get Help",
            ["ax-devil-device-api", "geocoordinates", "location", "get"],
            expected_in_help="Get current location coordinates"
        ),
        CommandTest(
            "Analytics Subcommand Help",
            ["ax-devil-device-api", "analytics"],
            expected_in_help="Manage analytics MQTT publishers"
        ),
        CommandTest(
            "Analytics Sources Help",
            ["ax-devil-device-api", "analytics", "sources"],
            expected_in_help="List available analytics data sources"
        ),
        CommandTest(
            "Discovery Subcommand Help",
            ["ax-devil-device-api", "discovery"],
            expected_in_help="Discover and inspect available discoverable APIs"
        ),
        CommandTest(
            "Discovery List Help",
            ["ax-devil-device-api", "discovery", "list"],
            expected_in_help="List all available APIs"
        ),
        CommandTest(
            "Features Subcommand Help", 
            ["ax-devil-device-api", "features"],
            expected_in_help="Manage device feature flags"
        ),
        CommandTest(
            "Features List Help",
            ["ax-devil-device-api", "features", "list"],
            expected_in_help="List all available feature flags"
        ),
        CommandTest(
            "Debug Subcommand Help",
            ["ax-devil-device-api", "debug"],
            expected_in_help="Manage device debugging operations"
        ),
    ]
    
    
    # Module import tests
    module_tests = [
        ("ax_devil_device_api.examples.main_cli", "Main CLI Module"),
        ("ax_devil_device_api.examples.device_info_cli", "Device Info CLI Module"),
        ("ax_devil_device_api.examples.network_cli", "Network CLI Module"),
        ("ax_devil_device_api.examples.media_cli", "Media CLI Module"), 
        ("ax_devil_device_api.examples.mqtt_client_cli", "MQTT CLI Module"),
        ("ax_devil_device_api.examples.ssh_cli", "SSH CLI Module"),
        ("ax_devil_device_api.examples.geocoordinates_cli", "Geocoordinates CLI Module"),
        ("ax_devil_device_api.examples.analytics_mqtt_cli", "Analytics CLI Module"),
        ("ax_devil_device_api.examples.api_discovery_cli", "Discovery CLI Module"),
        ("ax_devil_device_api.examples.feature_flags_cli", "Features CLI Module"),
        ("ax_devil_device_api.examples.device_debug_cli", "Debug CLI Module"),
        ("ax_devil_device_api.examples.cli_core", "CLI Core Module"),
    ]
    
    print("🔍 Testing module imports...")
    print("-" * 30)
    for module_path, test_name in module_tests:
        tester.run_import_test(module_path, test_name)
    
    print("\n🎯 Testing unified CLI commands...")
    print("-" * 40)
    for test in unified_cli_tests:
        tester.run_test(test)
    
    tester.print_summary()


if __name__ == "__main__":
    main()