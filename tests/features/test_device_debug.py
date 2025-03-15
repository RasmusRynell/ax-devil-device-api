import pytest
from src.ax_devil_device_api.utils.errors import FeatureError

@pytest.mark.integration
@pytest.mark.slow
def test_download_server_report(client):
    """Test downloading the server report returns binary data."""
    result = client.device_debug.download_server_report()
    assert isinstance(result, bytes), "Expected binary data for server report"


@pytest.mark.integration
@pytest.mark.slow
def test_download_crash_report(client):
    """Test downloading the crash report returns binary data."""
    result = client.device_debug.download_crash_report()
    assert isinstance(result, bytes), "Expected binary data for crash report"


@pytest.mark.integration
@pytest.mark.slow
def test_download_network_trace(client):
    """Test downloading network trace returns binary data."""
    # Test with default parameters
    result = client.device_debug.download_network_trace()
    assert isinstance(result, bytes), "Expected binary data for network trace"


@pytest.mark.integration
def test_ping_test_valid(client):
    """Test ping test with a valid target returns text."""
    result = client.device_debug.ping_test("8.8.8.8")
    assert isinstance(result, str), "Expected text data for ping test"


@pytest.mark.unit
def test_ping_test_invalid(client):
    """Test ping test with empty target returns error."""
    with pytest.raises(FeatureError):
        client.device_debug.ping_test("")


@pytest.mark.integration
def test_port_open_test_valid(client):
    """Test port open test with valid inputs returns text."""
    result = client.device_debug.port_open_test("8.8.8.8", 53)
    assert isinstance(result, str), "Expected text data for port open test"


@pytest.mark.unit
def test_port_open_test_invalid(client):
    """Test port open test with invalid inputs returns error."""
    with pytest.raises(FeatureError):
        client.device_debug.port_open_test("", 53)
