"""Test configuration and shared fixtures."""
import pytest
import os
from ax_devil_device_api import Client, DeviceConfig

def pytest_addoption(parser):
    """Add custom command line options for tests."""
    parser.addoption(
        "--run-restart",
        action="store_true",
        default=False,
        help="Run device restart tests (potentially disruptive)"
    )
    parser.addoption(
        "--protocol",
        choices=["http", "https"],
        default="https",
        help="Protocol to use for device communication (default: https)"
    )

def pytest_configure(config):
    """Configure test environment."""
    # Register custom markers
    config.addinivalue_line(
        "markers",
        "restart: mark test as requiring device restart (potentially disruptive)"
    )
    config.addinivalue_line(
        "markers",
        "skip_health_check: mark test to skip automatic health checks"
    )

def pytest_collection_modifyitems(config, items):
    """Skip restart tests unless explicitly enabled."""
    if not config.getoption("--run-restart"):
        skip_restart = pytest.mark.skip(reason="Need --run-restart option to run")
        for item in items:
            if "restart" in item.keywords:
                item.add_marker(skip_restart)

@pytest.fixture(scope="session")
def protocol(request):
    """Get the protocol to use for tests."""
    return request.config.getoption("--protocol")

@pytest.fixture(scope="session")
def client(protocol):
    """Create a client instance that persists for the entire test session."""
    device_ip = os.getenv("AXIS_TARGET_ADDR")
    device_user = os.getenv("AXIS_TARGET_USER")
    device_pass = os.getenv("AXIS_TARGET_PASS")

    if not all([device_ip, device_user, device_pass]):
        pytest.skip("Required environment variables not set")
    
    if protocol == "http":
        config = DeviceConfig.http(
            host=device_ip,
            username=device_user,
            password=device_pass
        )
    else:
        config = DeviceConfig.https(
            host=device_ip,
            username=device_user,
            password=device_pass,
            verify_ssl=False
        )
    
    client = Client(config)
    try:
        yield client
    finally:
        client.close()

@pytest.fixture(autouse=True)
def auto_health_check(request, client):
    """Automatically check device health before and after tests.
    
    By default, all tests get health checks. To skip health checks for a specific test:
        @pytest.mark.skip_health_check
        def test_something():
            # No health checks will run
            ...
    """
    if request.node.get_closest_marker('skip_health_check'):
        # Skip health check for tests that explicitly opt out
        yield
        return
        
    # Pre-test health check
    health = client.device.check_health()
    assert health.success, f"Pre-test health check failed: {health.error}"
    
    yield
    
    # Post-test health check
    health = client.device.check_health()
    assert health.success, f"Post-test health check failed: {health.error}" 